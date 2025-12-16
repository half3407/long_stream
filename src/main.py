# main.py
# 0. 安装依赖（一次性）：
#    pip install fastapi uvicorn


import datetime
from email.policy import HTTP
from fastapi import FastAPI, HTTPException
from fastapi import status
import uvicorn   # 帮我们省掉手写 JSON 解析的麻烦
from sentence import SentenceIn, SentenceOut;


# 1. 创建“纸面句子表”的内存替身
#    真实项目会用数据库，但先别管，把闭环跑通再说。
fake_db = {}


# 3. 生成 FastAPI 应用实例；app 这个名字别改，因为启动命令里用到了
app = FastAPI()

# 4. 全局自增 id 生成器，简单粗暴
#    重启服务计数器会归零，内存库也会清空——正适合初学阶段反复测试
current_id = 1

# 5. 实现“新增句子”接口
#    装饰器 @app.post 把函数注册成 POST /sentences 路由
@app.post("/sentences", response_model=SentenceOut)
def create_sentence(sentence: SentenceIn):
    """
    函数名随意，但参数名 sentence 必须和 SentenceIn 对应。
    FastAPI 会自动：
      - 把请求体 JSON 转成 SentenceIn 实例
      - 把返回值转成 JSON（按 SentenceOut 的字段）
    """
    global current_id
    new_sentence = {
    "id": current_id, 
    "content": sentence.content,
    "author": sentence.author}
    fake_db[current_id] = new_sentence   # 存进内存库
    current_id += 1
    return new_sentence                  # FastAPI 会按 SentenceOut 过滤字段

# 6. 实现“读取句子”接口
@app.get("/sentences/{sentence_id}", response_model=SentenceOut)
def read_sentence(sentence_id: int):
    """
    花括号里的 sentence_id 会自动从 URL 里提取并转成 int
    如果找不到，就抛 404，让前端知道这条记录不存在
    """
    sentence = fake_db.get(sentence_id)
    if not sentence:
        # HTTPException 会中断函数，直接返回 404 + 自定义文本
        raise HTTPException(status_code=404, detail="句子不存在")
    return sentence

# 7. 实现“删除句子”接口
@app.delete("/sentences/{sentence_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_sentence(sentence_id:int):
    if sentence_id not in fake_db:
        raise HTTPException(status_code=404, detail="句子不存在")
    del fake_db[sentence_id]

# 8. 实现“更新句子”接口
@app.put("/sentences/{sentence_id}", response_model=SentenceOut)
def update_sentence(sentence_id: int, sentence: SentenceIn):
    if sentence_id not in fake_db:
        raise HTTPException(status_code=404,detail="句子不存在")
    fake_db[sentence_id] = {
        "id": sentence_id,
        "content": sentence.content,
        "author": sentence.author
    }
    return fake_db[sentence_id]

# 9. 实现“列出所有句子”接口
@app.get("/sentences", response_model=list[SentenceOut])
def list_sentences():
    """
    列出所有句子
    """
    return list(fake_db.values())

# 程序主入口
if __name__ == "__main__":
    # 初始化日志
    from long_stream.log import init_logger,logger
    # 以当前时间命名日志文件，避免覆盖旧日志
    init_logger(f"long_stream_{datetime.date.today()}.log")
    logger.info("应用启动中...")
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
    )