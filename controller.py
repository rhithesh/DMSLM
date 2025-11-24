from parentClass.main import DMSLMMain
from mlmodels.main import dMonitoring
from llmclass.main import LLMClass
from pipertts.main import PiperTTS
from helper.chat import Helper
from whispermodule.main import VoiceInput

import threading

def create_controller():
    controller = DMSLMMain()

    monitor = dMonitoring(controller)
    llm = LLMClass(controller)
    tts = PiperTTS(controller)
    helper = Helper(controller)
    voice = VoiceInput(controller)

    return controller, monitor, llm, tts, helper, voice
