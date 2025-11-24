
import queue
import time
import threading
class  DMSLMMain():


    def __init__(self):
        self.UserCanSpeak=False
        self.chattingwithllm=False
        self.messages=[]
        self.LLMSTART=False
        self._last_messages_count=0
        self.imageQueue=queue.Queue()
        print("Created Image Queue")
        self.processdImageJsonQueue=queue.Queue()
        self.textOutputQueue=queue.Queue()
        print("Created ProcessedImageJson Queue")
        threading.Thread(target=self.display_queue, daemon=True).start()


    def display_queue(self):
        while True:
            print("ID", id(self))
            print(self.messages)

            time.sleep(1)


        








