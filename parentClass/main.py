
import queue
import time
class  DMSLMMain():


    def __init__(self):
        self.chattingwithllm=False
        self.messages=[]
        self.imageQueue=queue.Queue()
        print("Created Image Queue")
        self.processdImageJsonQueue=queue.Queue()
        self.textOutputQueue=queue.Queue()
        print("Created ProcessedImageJson Queue")

    def display_queue(self):
        while True:
            print("imgQueue:", self.imageQueue.qsize(),"imagejsonsize:",self.processdImageJsonQueue.qsize())
            time.sleep(1)   # update every 100ms

        








