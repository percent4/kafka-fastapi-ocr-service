本项目使用Kafka作为消息队列，FastAPI作Web框架，来模拟图片OCR实现。主要功能如下：

1. 上传图片到FastAPI，FastAPI将图片发送到Kafka，同时将图片信息写入数据库，状态为未完成
2. Kafka消费者消费图片，调用模拟的OCR识别结果，将结果更新至数据库，状态为已完成
3. FastAPI查询数据库，返回识别结果

流程图如下：

![主流程示意图](https://s2.loli.net/2025/02/07/PD3Cd9ubp4zqrW7.png)

## 前端页面

前端页面采用BootStrap实现，位于`static`目录，主要功能如下：

- 批量上传图片页面: upload.html
- 查询图片识别结果页面: results.html

前端代码使用使用OpenAI GPT-4o模型生成，代码略作修改，功能完整。

## 后端代码

- Web框架使用FastAPI实现
- 数据库使用MySQL实现
- 消息队列使用Kafka实现

## 项目启动

1. 安装并启动Kafka，在Kafka中创建名为`ocr-topic`的topic
2. 安装并启动MySQL，创建数据库`ocr`，使用src/models.py创建表`ocr_results`
3. 安装依赖包：`pip install -r requirements.txt`
4. 运行Kafka消费者: `python src/consumer.py`
5. 启动FastAPI：

```shell
cd src
cuvicorn src.main:app --reload
```

## 项目效果

1. 批量上传图片页面

![](https://s2.loli.net/2025/02/07/zmJNMbFklcDEOCg.png)

2. 未识别前的MySQL数据库中的数据

![](https://s2.loli.net/2025/02/08/KFAgUVn8LlGDcob.png)

3. 未识别前的OCR结果查看页面

![](https://s2.loli.net/2025/02/08/zC6SqV9X73NtsQB.png)


4. 识别后的MySQL数据库中的数据

![](https://s2.loli.net/2025/02/08/Kwrsiu6cEtUL2vN.png)

5. 识别后的OCR结果查看页面

![](https://s2.loli.net/2025/02/08/MI7JWE9ir5gL4ve.png)

6. Kafka中的消息查看

![](https://s2.loli.net/2025/02/08/rQEMuUTfsYo1bSW.png)

7. 查看图片

![](https://s2.loli.net/2025/02/08/93mTvKc4rx1jUhB.png)