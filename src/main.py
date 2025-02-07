# -*- coding: utf-8 -*-
# @place: Pudong, Shanghai
# @file: main.py
# @time: 2025/2/7 16:59
import os
import uuid
import time
from datetime import datetime as dt
from fastapi import FastAPI, File, UploadFile, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import SessionLocal, OCRResult
from starlette.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config import KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC

from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=f'{KAFKA_HOST}:{KAFKA_PORT}')

app = FastAPI()

# 允许前端访问 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_FOLDER = "static"
UPLOAD_FOLDER = f"{STATIC_FOLDER}/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# **提供静态资源**
app.mount("/static", StaticFiles(directory=STATIC_FOLDER), name="static")


# **首页 `/` 自动打开上传页面**
@app.get("/")
async def serve_homepage():
    return FileResponse("static/upload.html")


# 依赖项：数据库会话管理
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# **📌 上传文件并 OCR 识别**
@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    start_time = time.time()

    # **生成唯一 ID 并保存文件**
    file_extension = file.filename.split(".")[-1]
    unique_id = str(uuid.uuid4())  # 生成 UUID 作为文件唯一标识
    save_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.{file_extension}")

    with open(save_path, "wb") as image_file:
        image_file.write(file.file.read())

    # **使用 Tesseract OCR 识别图片文字**
    # image = Image.open(save_path)
    # ocr_text = pytesseract.image_to_string(image)

    elapsed_time = time.time() - start_time  # 计算处理时间

    # **存储 OCR 结果到数据库**
    db_result = OCRResult(
        uuid=unique_id,
        filename=file.filename,
        filepath=save_path,
        ocr_text=None,
        start_time=dt.now(),
        status=0,
        elapsed_time=0.0
    )
    db.add(db_result)
    db.commit()

    # 将uuid和文件路径送入至Kafka队列，作为生产者
    producer.send(KAFKA_TOPIC, key=unique_id.encode(), value=save_path.encode())

    return {
        "uuid": unique_id,
        "filename": file.filename,
        "ocr_text": None,
        "elapsed_time": elapsed_time
    }


# **📌 获取所有 OCR 结果**
@app.get("/results/")
def get_results(
    db: Session = Depends(get_db),
    filename: str = Query(None, title="文件名", description="搜索 OCR 记录的文件名"),
    sort_by_time: bool = Query(False, title="按时间排序", description="是否按时间倒序排序")
):
    query = db.query(OCRResult)

    # **🔍 文件名搜索**
    if filename:
        query = query.filter(OCRResult.filename.contains(filename))

    # **🕒 按时间倒序**
    if sort_by_time:
        query = query.order_by(OCRResult.start_time.desc())

    results = query.all()

    return [
        {
            "uuid": result.uuid,
            "filename": result.filename,
            "filepath": f"uploads/{os.path.basename(result.filepath)}",
            "ocr_text": result.ocr_text,
            "start_time": result.start_time.strftime("%Y-%m-%d %H:%M:%S"),  # 🎯 格式化时间
            "status": "已完成" if result.status else "进行中",
            "elapsed_time": result.elapsed_time,
        }
        for result in results
    ]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    # 启动 FastAPI 服务
    # uvicorn main:app --reload
