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

# ✅ Root route for health check
@app.get("/")
async def root():
    return {"message": "Safe Stream Backend is running"}

@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    try:
        video_path = f"uploaded_{file.filename}"
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        results = analyze_video(video_path)
        os.remove(video_path)

        status = "unsafe" if results else "safe"
        return JSONResponse(content={"status": status, "results": results})

    except Exception as e:
        print(f"❌ Error: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# ✅ Optional: for local testing only
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

