from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from controller import create_controller  
import warnings
warnings.filterwarnings("ignore")

app = FastAPI()

DSLMController, monitor, llm, tts, helper, voice = create_controller()


@app.post("/image")
async def image(
    image: UploadFile = File(...),
    time: str = Form(...)
):
    try:

        content = await image.read()

        DSLMController.imageQueue.put({
            "filename": image.filename,
            "time": time,
            "bytes": content,
        })

        return {"msg": "queued"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
