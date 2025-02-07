# -*- coding: utf-8 -*-
# @place: Pudong, Shanghai
# @file: models.py
# @time: 2025/2/7 16:59
from sqlalchemy import Column, Integer, String, Float, create_engine, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config

# 定义 MySQL 连接 URL
DATABASE_URL = f"mysql+pymysql://{config.MYSQL_USERNAME}:{config.MYSQL_PASSWORD}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DATABASE}"

# 连接 MySQL
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 定义 OCR 结果的数据库表
class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uuid = Column(String(255), unique=True, index=True)
    filename = Column(String(255), index=True)
    filepath = Column(String(512))
    ocr_text = Column(String(5000))  # OCR 处理可能会返回较长文本
    start_time = Column(DATETIME)  # 记录开始时间
    status = Column(Integer)  # 0-未完成；1-已完成
    elapsed_time = Column(Float)  # 记录消耗时间, 单位秒


if __name__ == "__main__":
    # 确保创建表
    Base.metadata.create_all(bind=engine)
