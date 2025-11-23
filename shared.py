from parentClass.main import DMSLMMain
import threading
from mlmodels.main import dMonitoring
from llmclass.main import LLMClass
from pipertts.main import PiperTTS
from helper.chat import Helper

DSLMController = DMSLMMain()

threading.Thread(target=DSLMController.display_queue, daemon=True).start()
drivermonitor=dMonitoring(DSLMController)
threading.Thread(target=drivermonitor.continuscheck, daemon=True).start()




llmmonitor=LLMClass(DSLMController)
threading.Thread(target=llmmonitor.analyze_llm_call_need, daemon=True).start()

PiperTTS=PiperTTS(DSLMController)
# not using threading Thread because it is being initialized int __init__ method 

helper=Helper(DSLMController)



