# -*- coding: utf-8 -*-
# @place: Pudong, Shanghai
# @file: consumer.py
# @time: 2025/2/7 19:20
import time
import string
from random import random, choice, randint
from kafka import KafkaConsumer

from models import SessionLocal, OCRResult
from config import KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC


db = SessionLocal()

consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=f'{KAFKA_HOST}:{KAFKA_PORT}')
for message in consumer:
    start_time = time.time()
    file_uuid = message.key.decode()
    file_path = message.value.decode()
    time.sleep(random() * 10)  # 模拟 OCR 识别耗时
    # 将模拟的 OCR 结果更新至数据库，更新的筛选条件是 uuid
    chars = randint(3, 20)
    result = []
    for _ in range(chars):
        result.append(choice(string.digits + string.ascii_letters))

    db.query(OCRResult).filter(OCRResult.uuid == file_uuid).update(
        {
            "ocr_text": "".join(result),
            "status": 1,
            "elapsed_time": time.time() - start_time
        }
    )
    db.commit()
