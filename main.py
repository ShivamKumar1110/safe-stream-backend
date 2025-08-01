from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from nsfw_api import analyze_video  # ✅ Make sure nsfw_api.py is in same folder

app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    try:
        video_path = f"uploaded_{file.filename}"
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        results = analyze_video(video_path)
        os.remove(video_path)

        status = "unsafe" if results else "safe"  # ✅ NEW LINE
        return JSONResponse(content={"status": status, "results": results})  # ✅ MODIFIED

    except Exception as e:
        print(f"❌ Error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)
