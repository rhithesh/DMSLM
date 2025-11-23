from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from shared import DSLMController

app = FastAPI()

@app.post("/image")
async def image(
    image: UploadFile = File(...),
    time: str = Form(...)
):
    try:
        # Read binary JPG bytes
        content = await image.read()

        # Put into queue: both image and timestamp

        DSLMController.imageQueue.put({
            "filename": image.filename,
            "time": time,
            "bytes": content,
        })


        return {"msg": "queued"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
