from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from controller import create_controller  
import warnings
from fastapi.middleware.cors import CORSMiddleware
import json

warnings.filterwarnings("ignore")
from fastapi.responses import StreamingResponse

app = FastAPI()

DSLMController, monitor, llm, tts, helper, voice = create_controller()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

        return JSONResponse(content={"msg": "queued"}, status_code=200)


    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

def event_stream():
    """Blocking generator that waits for items in the queue"""
    while True:
        data = DSLMController.event_queue.get()   # waits until something is available
        print(data,"Helloo")
        yield f"data: {json.dumps(data)}\n\n"



@app.get("/stream")
async def stream():
    return StreamingResponse(event_stream(), media_type="text/event-stream")
