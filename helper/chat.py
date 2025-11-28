import requests
import json
import os

class Helper:
    def __init__(self, main):
        self.main = main
        self.api_key = ""
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set!")
        
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "meta-llama/llama-3.3-70b-instruct"
    
    def chatLLM(self, messages):
        """
        Stream chat completion from OpenRouter using Llama 3.3 70B
        messages: [{"role": "system/user/assistant", "content": "..."}]
        """
        print(f"🦙 Sending request to Llama 3.3 70B via OpenRouter...")

        
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": 0.7,  # Optional: adjust for more/less creative responses
            "max_tokens": 100    # Optional: keep responses brief for driving safety
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://driver-monitor.local",
            "X-Title": "Driver Monitoring System"
        }
        
        try:
            self.main.UserCanSpeak=False
            response = requests.post(
                self.url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=30  # 30 second timeout
            )
            
            if response.status_code != 200:
                print(f"❌ OpenRouter API error: {response.status_code}")
                print(f"Response: {response.text}")
                return
            
            print("✅ Streaming response...")
            _data_to_append_messages=""
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    
                    if decoded_line.startswith("data: "):
                        data = decoded_line.replace("data: ", "")
                        
                        if data == "[DONE]":
                            self.main.textOutputQueue.put(None)

                            
                            print("\n✅ Response complete")
                            break
                        
                        try:
                            chunk = json.loads(data)
                            delta = chunk["choices"][0]["delta"].get("content", "")
                            if delta:
                                print(delta, end="", flush=True)
                                _data_to_append_messages+=delta
                                self.main.textOutputQueue.put(delta)
                        
                        except (json.JSONDecodeError, KeyError) as e:
                            continue
            self.main.messages.append({"role": "assistant","content": _data_to_append_messages})
            print("Let is where we are",self.main.messages[-1])


        
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
        except Exception as e:
            print(f"❌ Error calling OpenRouter: {e}")
            import traceback
            traceback.print_exc()