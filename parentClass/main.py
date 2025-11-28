
import queue
import time
import threading
import json
class  DMSLMMain():


    def __init__(self):
        self.UserCanSpeak=True
        self.chattingwithllm=False
        self.messages=[{
                        "role": "system",
                         "content": "You are a friendly driving voice assistant that helps keep drivers alert and safe. Keep your messages short and conversational. Your response is directly converted to speech so avoid bullet points, lists, or special formatting."
                        }]
        self.firstLLMtrigger=False
        self._last_messages_count=0
        self.imageQueue=queue.Queue()
        self.processdImageJsonQueue=queue.Queue()
        self.textOutputQueue=queue.Queue()
        self.event_queue=queue.Queue()
        threading.Thread(target=self.display_queue, daemon=True).start()


    def display_queue(self):
        while True:
            print(json.dumps(self.messages, indent=4))
            print("                 User   can speak                    ",self.UserCanSpeak      )            

            time.sleep(3)


        








