
from helper.chat import Helper

import os

from parentClass.main import DMSLMMain

class LLMClass(DMSLMMain):
    """A class which keeps analyzing the current input whether the drivers eyes are open or closed and over time if the speaker is attentive it speaks to it normally."""
    def __init__(self,main):
        self.main=main
        self.closed_counter=0
        self.helper = Helper(main)

        print("Hello my name is Hithesh R")
        


    def greet(self):
        return "Hello from LLMClass!"
    
    def analyze_llm_call_need(self):
        
        while True:
            try:
                obj = self.main.processdImageJsonQueue.get()
                left = obj["left_eye"]
                right = obj["right_eye"]
                if left == "closed" and right == "closed":
                    self.closed_counter += 1
                else:
                    self.closed_counter = 0
                print(f"[LLM] Eyes: L={left} R={right} | closed_count={self.closed_counter}")
                
                if self.closed_counter > 8:
                    try:

                        message = f"The driver seems to be drowsy. Closed eye frames 8/30 frames per second his eyes were closed: {self.closed_counter}, Start a Conversation and please let me know if the driver is drowsy or not."
                        print("⚠️ ", message)
                        content = f"The driver seems to be drowsy. Their eyes were closed for {self.closed_counter} consecutive frames out of 30 fps. Start a conversation to check if they are alert."
                        messages = [{
                        "role": "system",
                        "content": "You are a friendly driving assistant that helps keep drivers alert and safe."
                        },
                        {
                        "role": "user",
                        "content": content
                        }
                        ]

                        self.helper.chatLLM(messages)
                    except Exception as e:
                        print("Error calling LLM:", e)
                closed_counter = 0
                
            except Exception as e:
               # print("🔥 Error in analyze_llm_call_need:", e)
                continue

    
        

        #logic to analyze continuos incomming stream of data


        
        

    