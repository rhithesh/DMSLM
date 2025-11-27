import sounddevice as sd
import numpy as np
import queue
import time
import threading
from silero_vad import load_silero_vad, get_speech_timestamps
from faster_whisper import WhisperModel
from parentClass.main import DMSLMMain

class VoiceInput(DMSLMMain):
    def __init__(self, main, device_index=3):
        self.main = main
        self.device_index = device_index
        
        # Audio settings
        self.SAMPLE_RATE = 16000
        self.BLOCK_SIZE = 1024
        self.WINDOW_SIZE = int(self.SAMPLE_RATE * 1.5)  # 1.5 second window
        self.SILENCE_TIMEOUT = 0.5
        
        # Queues and buffers
        self.audio_queue = queue.Queue()
        self.vad_buffer = np.array([], dtype=np.float32)
        self.speech_buffer = np.array([], dtype=np.float32)
        
        # State tracking
        self.last_voice_time = time.time()
        self.speaking = False
        self.stop_event = threading.Event()
        
        # Load models
        print("Loading Whisper and VAD models...")
        self.whisper_model = WhisperModel("base.en", device="cpu", compute_type="int8")
        self.vad_model = load_silero_vad()
        print("✅ Models loaded")
        
        # Start listening thread
        self.listener_thread = threading.Thread(target=self._listen, daemon=True)
        self.listener_thread.start()
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio input stream"""
        if status:
            print(f"Audio status: {status}")
        self.audio_queue.put(indata.copy())
    
    def _listen(self):
        print("🎤 Voice input started. Listening...")



        with sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            blocksize=self.BLOCK_SIZE,
            channels=1,
            dtype="float32",
            callback=self._audio_callback,
            device=self.device_index
        ):
            while not self.stop_event.is_set():

                
                # Freeze listening if speaking not allowed
                if not self.main.UserCanSpeak:
                    #notfalse is true #by default It is true
                    time.sleep(0.2)
                    continue

                

                try:
                    chunk = self.audio_queue.get(timeout=0.1)
                    self._process_audio_chunk(chunk)

                except queue.Empty:
                    if self.speaking and time.time() - self.last_voice_time > self.SILENCE_TIMEOUT:
                        self._transcribe_and_send()
                    continue
                except Exception as e:
                    print(f"Error in listen loop: {e}")
                    import traceback
                    traceback.print_exc()

    
    
    def _process_audio_chunk(self, chunk):
        """Process incoming audio chunk for VAD"""
        # Flatten chunk to ensure 1D array
        chunk_flat = chunk.flatten()
        
        # Add to VAD buffer (sliding window)
        self.vad_buffer = np.append(self.vad_buffer, chunk_flat)
        if len(self.vad_buffer) > self.WINDOW_SIZE:
            self.vad_buffer = self.vad_buffer[-self.WINDOW_SIZE:]
        
        # Convert to int16 for VAD
        audio_int16 = (self.vad_buffer * 32767).astype(np.int16)
        
        # Ensure it's a 1D array
        if audio_int16.ndim == 0:
            audio_int16 = np.array([audio_int16])
        elif audio_int16.ndim > 1:
            audio_int16 = audio_int16.flatten()
        
        # Check for speech
        timestamps = get_speech_timestamps(
            audio_int16,
            self.vad_model,
            sampling_rate=self.SAMPLE_RATE
        )
        
        has_speech = len(timestamps) > 0
        
        if has_speech:
            # If just started speaking, clear old speech buffer
            if not self.speaking:
                print("🎤 Speech detected, recording...")
                self.speech_buffer = np.array([], dtype=np.float32)
                self.speaking = True
            
            # Accumulate all audio while speaking
            self.speech_buffer = np.append(self.speech_buffer, chunk_flat)
            self.last_voice_time = time.time()
        
        # Check for silence after speech
        if self.speaking and not has_speech and time.time() - self.last_voice_time > self.SILENCE_TIMEOUT:
            self._transcribe_and_send()
    def _transcribe_and_send(self):
        """Transcribe accumulated speech and send to messages"""
        self.speaking = False
        
        duration = len(self.speech_buffer) / self.SAMPLE_RATE
        print(f"🎤 Transcribing... ({duration:.1f}s of audio)")
        
        if len(self.speech_buffer) > 0:
            try:
                # Convert accumulated speech to int16 then float32 for Whisper
                speech_int16 = (self.speech_buffer * 32767).astype(np.int16)
                audio_float = speech_int16.astype(np.float32) / 32767.0
                
                # Transcribe
                segments, _ = self.whisper_model.transcribe(audio_float)
                text = "".join([s.text for s in segments]).strip()
                

                #this is happening aldready
                if text:
                    print(f"🎤 User said: {text}")
                    
                    # Add user message to conversation history
                    user_message = {
                        "role": "user",
                        "content": text
                    }
                    
                    if not hasattr(self.main, 'messages'):
                        self.main.messages = [
                            {
                                "role": "system",
                                "content": "You are a friendly driving voice assistant that helps keep drivers alert and safe. Keep your messages short and conversational. Your response is directly converted to speech so avoid bullet points, lists, or special formatting."
                            }
                        ]
                    
                    # Append user message
                    self.main.messages.append(user_message)


                    try:
                        print("Is this happening")
                        from server import helper
                        helper.chatLLM(self.main.messages)
                    except Exception as e:
                        print("LLM error",{e})

                    

                    
                    
                    print(f"✅ Added to conversation (total messages: {len(self.main.messages)})")
                    
                    # Trigger LLM to respond
                    if hasattr(self.main, 'voiceInputQueue'):
                        self.main.voiceInputQueue.put(text)  # Signal new voice input
                    
                else:
                    print("(no speech detected)")
                    
            except Exception as e:
                print(f"❌ Transcription error: {e}")
                import traceback
                traceback.print_exc()
        
        # Reset buffers
        self.speech_buffer = np.array([], dtype=np.float32)
        self.vad_buffer = np.array([], dtype=np.float32)
        print("🎤 Ready for next input...\n")
    


    def stop(self):
        """Stop listening"""
        print("Stopping voice input...")
        self.stop_event.set()
        self.listener_thread.join(timeout=2)