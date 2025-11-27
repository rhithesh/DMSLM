from parentClass.main import DMSLMMain
from piper import PiperVoice
import re
import sounddevice as sd
import numpy as np
import threading
import queue

class PiperTTS(DMSLMMain):

    def __init__(self, main):
        self.main = main
        self.voice = PiperVoice.load(
            model_path="voiceagentpiper/en_US-amy-medium.onnx",
            config_path="voiceagentpiper/config.json"
        )

        self.stop_event = threading.Event()
        self.audio_queue = queue.Queue()

        # Start BOTH threads
        self.text_processor_thread = threading.Thread(target=self._process_text, daemon=True)
        self.text_processor_thread.start()
        
        self.audio_player_thread = threading.Thread(target=self._play_audio, daemon=True)
        self.audio_player_thread.start()

    def _process_text(self):
        buffer = ""

        while not self.stop_event.is_set():
            try:
                chunk = self.main.textOutputQueue.get(timeout=0.1)  # FIX: Added timeout

                if chunk is None:
                    if buffer.strip():
                        self._synthesize_and_queue(buffer)
                    break  # FIX: Added break to exit loop

                buffer += chunk

                sentences = re.split(r'(?<=[.!?])\s+', buffer)
                
                # FIX: Process complete sentences
                if len(sentences) > 1:
                    for sentence in sentences[:-1]:
                        if sentence.strip():
                            print(f"Speaking: {sentence}")
                            self._synthesize_and_queue(sentence)
                    buffer = sentences[-1]

            except queue.Empty:  # FIX: Changed from self.main.textOutputQueue.Empty
                continue
            except Exception as e:
                print(f"Text processing error: {e}")  # FIX: Added {e}
                import traceback
                traceback.print_exc()

    def _synthesize_and_queue(self, text):
        """Synthesize text and add to audio queue"""
        try:
            audio_chunks = []  # FIX: spelling
            
            for chunk in self.voice.synthesize(text):  # FIX: spelling (was synthezize)
                audio_chunks.append(chunk.audio_int16_bytes)

            if audio_chunks:
                combined_audio = b"".join(audio_chunks)
                print(f"Queued audio: {len(combined_audio)} bytes")
                self.audio_queue.put(combined_audio)
        except Exception as e:
            print(f"Synthesis error: {e}")
            import traceback
            traceback.print_exc()

    def _play_audio(self):
        """Play audio chunks as they become available"""

        while not self.stop_event.is_set():
            try:
                audio_data = self.audio_queue.get()
                if audio_data is None:
                    print("OKay now user Can speak")
                    self.main.UserCanSpeak=True
                    break

                print(f"Playing audio: {len(audio_data)} bytes")

                try:
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                    audio_float = audio_array.astype(np.float32) / 32768.0  # FIX: 32768, not 32168 and wrong syntax

                    sd.play(audio_float, samplerate=22050, blocking=True)
                    print("Audio playback complete")
                    


           


                except Exception as e:
                    print(f"Audio play error: {e}")  # FIX: Added f-string
                    import traceback
                    traceback.print_exc()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Playback error: {e}")
                import traceback
                traceback.print_exc()

    def finish(self):
        """Call this when done to clean up"""
        self.main.UserCanSpeak=True
        self.main.textOutputQueue.put(None)  # Signal text processor to finish
        self.text_processor_thread.join()
        
        self.audio_queue.put(None)  # Signal audio player to finish
        self.audio_player_thread.join()