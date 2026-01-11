from dotenv import load_dotenv
# 导入生效环境变量配置
load_dotenv()
import os
import datetime
import uvicorn
from log import init_logger, logger
from fastapi import  FastAPI, Request
from db.database import init_db
from controls.ctl_sentence import sentence_router
from controls.ctl_user import user_router

LONG_STREAM_ENVS = [env for env in os.environ if env.startswith("LONG_STREAM_")]
LONG_STREAM_ENV_DICT = {env: os.environ.get(env) for env in LONG_STREAM_ENVS}
print(f"[DEBUG] 当前环境变量: {LONG_STREAM_ENV_DICT}")

ROOT_ROUTER_PREFIX=os.environ.get("LONG_STREAM_ROOT_ROUTER_PREFIX","/api/v1")

app = FastAPI(version="1.0.0", title="Long Stream API")

# 在模块导入时注册路由，这样使用 uvicorn 导入模块时也能正确生成 OpenAPI
router_list = [sentence_router, user_router]

app.include_router(sentence_router, prefix=f"{ROOT_ROUTER_PREFIX}")
app.include_router(user_router, prefix=f"{ROOT_ROUTER_PREFIX}/auth")

# 程序主入口
if __name__ == "__main__":
    # 初始化日志
    # 以当前时间命名日志文件，避免覆盖旧日志
    logger.info("应用启动中...")
    init_logger(f"long_stream_{datetime.date.today()}.log")
    logger.info("初始化数据库...")
    init_db()
    logger.info("数据库初始化完成。")

    for router in router_list:
        for sub_router in router.routes:
            print(f"已注册路由:[{tuple(sub_router.methods)[0]}] {ROOT_ROUTER_PREFIX}{sub_router.path}") # type: ignore
            
    uvicorn.run(
        "main:app",
        host=os.environ.get("LONG_STREAM_SERVER_HOST", "localhost"),
        port=int(os.environ.get("LONG_STREAM_SERVER_PORT", "8000")),
    )