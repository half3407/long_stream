import datetime
from fastapi.routing import APIRoute
import uvicorn
from log import init_logger,logger
from fastapi import APIRouter, FastAPI
from db.database import init_db
from controls.ctl_sentence import sentence_router
from controls.ctl_user import user_router
ROOT_ROUTER_PREFIX="/api/v1"

app = FastAPI(version="1.0.0", title="Long Stream API", root_path=ROOT_ROUTER_PREFIX)

test_router = APIRouter()

@test_router.get("/ping")
def ping():
    return {"message": "pong"}

# 程序主入口
if __name__ == "__main__":
    # 初始化日志
    # 以当前时间命名日志文件，避免覆盖旧日志
    logger.info("应用启动中...")
    init_logger(f"long_stream_{datetime.date.today()}.log")
    logger.info("初始化数据库...")
    init_db()
    logger.info("数据库初始化完成。")
    
    router_list = [sentence_router, user_router, test_router]

    for router in router_list:
        app.include_router(router=router)
        [logger.info(f"已注册路由:[{tuple(sub_router.methods)[0]}] {ROOT_ROUTER_PREFIX}{sub_router.path}") for sub_router in router.routes] # type: ignore

    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
    )