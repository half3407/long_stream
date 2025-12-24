import datetime
import uvicorn
from long_stream.log import init_logger, logger
from fastapi import  FastAPI
from long_stream.db.database import init_db
from long_stream.controls.ctl_sentence import sentence_router
from long_stream.controls.ctl_user import user_router
ROOT_ROUTER_PREFIX=""

app = FastAPI(version="1.0.0", title="Long Stream API", root_path=ROOT_ROUTER_PREFIX)

# 在模块导入时注册路由，这样使用 uvicorn 导入模块时也能正确生成 OpenAPI
router_list = [sentence_router, user_router]

for router in router_list:
    app.include_router(user_router, prefix="/api/v1/auth")

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
        [logger.info(f"已注册路由:[{tuple(sub_router.methods)[0]}] {ROOT_ROUTER_PREFIX}{sub_router.path}") for sub_router in router.routes] # type: ignore

    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
    )