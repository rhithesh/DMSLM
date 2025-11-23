from parentClass.main import DMSLMMain
import threading
from mlmodels.main import dMonitoring
from llmclass.main import LLMClass
from pipertts.main import PiperTTS
from helper.chat import Helper
import time

DSLMController = DMSLMMain()

threading.Thread(target=DSLMController.display_queue, daemon=True).start()
drivermonitor = dMonitoring(DSLMController)
threading.Thread(target=drivermonitor.continuscheck, daemon=True).start()

llmmonitor = LLMClass(DSLMController)
threading.Thread(target=llmmonitor.analyze_llm_call_need, daemon=True).start()

PiperTTS = PiperTTS(DSLMController)

helper = Helper(DSLMController)

print("System running... Press Ctrl+C to stop")

# Keep main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down...")
    DSLMController.stop()  # If you have a stop method
    PiperTTS.stop_event.set()