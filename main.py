import os
import uuid
import edge_tts
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.background import BackgroundTasks

app = FastAPI()

class TTSRequest(BaseModel):
    text: str
    voice: str = "vi-VN-HoaiMyNeural"

def cleanup(path: str):
    if os.path.exists(path):
        os.remove(path)

@app.post("/tts")
async def generate_tts(request: TTSRequest, background_tasks: BackgroundTasks):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Văn bản trống")

    file_path = f"{uuid.uuid4()}.mp3"
    try:
        # Log đơn giản để Ngài theo dõi trên Render sau này
        print(f"🚀 Đang tạo: {len(request.text)} ký tự | Giọng: {request.voice}")
        
        communicate = edge_tts.Communicate(request.text, request.voice)
        await communicate.save(file_path)
        
        file_size = os.path.getsize(file_path)
        print(f"✅ Thành công: {file_size} bytes")

        background_tasks.add_task(cleanup, file_path)
        return FileResponse(file_path, media_type="audio/mpeg")
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        if os.path.exists(file_path): os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))
