from fastapi import FastAPI
app = FastAPI()

@app.get("/")  # 必须有这个基础路由
async def root():
    return {"message": "Hello World"}