
import queue
import time
import threading
class  DMSLMMain():


    def __init__(self):
        self.UserCanSpeak=False
        self.chattingwithllm=False
        self.messages=[{
                        "role": "system",
                        "content": "You are a friendly driving assistant that helps keep drivers alert and safe,PLEASE GIVE YOUR RESPONSE IN AS A VOICE CHATBOT."
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
            print("ID", id(self))
            # print({
            #     "UserCanSpeak":self.UserCanSpeak,
            #     "firstLLtrigger":self.firstLLMtrigger,
            #     "messages":self.messages})

            time.sleep(1)


        








