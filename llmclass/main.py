
from helper.chat import Helper

import os
import threading

from parentClass.main import DMSLMMain

class LLMClass(DMSLMMain):
    """A class which keeps analyzing the current input whether the drivers eyes are open or closed and over time if the speaker is attentive it speaks to it normally."""
    def __init__(self,main):
        self.main=main
        self.closed_counter=0
        self.helper = Helper(main)
        self.stoper=1
        threading.Thread(target=self.analyze_llm_call_need, daemon=True).start()


        


    def greet(self):
        return "Hello from LLMClass!"
    
    def analyze_llm_call_need(self):
        print("Started analyze LLM Function")
        
        while True:
            try:
                obj = self.main.processdImageJsonQueue.get()
                left = obj["left_eye"]
                right = obj["right_eye"]
                if left == "closed" and right == "closed":
                    self.closed_counter += 1
                    self.main.event_queue.put({"closed_counter":self.closed_counter})
                else:
                    self.closed_counter = 0
                #print(f"[LLM] Eyes: L={left} R={right} | closed_count={self.closed_counter}",{self.main.firstLLMtrigger})
                print(self.closed_counter)
                if self.closed_counter > 3:
                    
                    try:
                

                        message = f"The driver seems to be drowsy. Closed eye frames 8/30 frames per second his eyes were closed: {self.closed_counter}, Start a Conversation and please let me know if the driver is drowsy or not."
                        print("⚠️ ", message)
                        content = f"The driver seems to be drowsy. Their eyes were closed for {self.closed_counter} consecutive frames out of 30 fps. Start a conversation to check if they are alert, Remeber you are an voice assistant you have to give pure voice output."
                        messages = [
                        {
                        "role": "user",
                        "content": content
                        }
                        ]
                        if len(self.main.messages)==0:
                            self.main.messages.extend(messages)
                        self.main.firstLLMtrigger=True




                        if  self.main.firstLLMtrigger:
                            self.main.firstLLMtrigger=False
                            print("We are here")
                            self.stoper=0
                            self.helper.chatLLM(self.main.messages)
                            print("LLM HAS BEEN Triggered")
                            self.main.event_queue({"llm_Status":"active"})

                    except Exception as e:
                        print("Error calling LLM:", e)
                
            except Exception as e:
                print("Error in analyze_llm_call_need:", e)
                continue

    
        

        #logic to analyze continuos incomming stream of data


        
        

    