from loguru import logger

# 这里定义日志轮转大小和保留天数的常量
# 常量的特点就是全部大写，方便识别
# 这里定义常量也有好处是方便给其他地方使用 （可以先保留我这里没有例子演示，说不定后续有）
ROTATION_SIZE = "5 MB"
RETENTION_DAYS = 5
LOG_LEVEL = "INFO"  # 默认日志等级


def init_logger(log_file: str = "app.log", level: str = LOG_LEVEL):
    """
    初始化日志配置.

    Args:
        log_file (str): The file to which logs will be written.
        level (str): The logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR").
    """
    # unuse default logger 不使用默认日志（python默认会有一个日志系统。这里我们不用默认的，所以先取消使用它）
    logger.remove()

    # 设置日志配置
    # 日志文件大小达到5 MB时轮转，保留5天的日志，并压缩旧日志
    # 添加日志文件与配置日志等级
    logger.add(
        log_file,
        level=level,
        rotation=ROTATION_SIZE,
        retention=RETENTION_DAYS,
        compression="zip",
    )

    # 添加控制台输出
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=level,
    )

    # 日志等级解释:
    # DEBUG: 详细信息，通常只在诊断问题时使用
    # INFO: 确认程序按预期工作的信息
    # WARNING: 表明发生了意外情况，或表明在不久的将来会出现某种问题（例如“磁盘空间不足”）。软件仍然按预期工作。
    # ERROR: 由于更严重的问题，软件已不能正常运行

    # 例如当前日志等级是 INFO，则会记录 INFO、WARNING 和 ERROR 级别的日志，DEBUG 级别的日志不会被记录
    # 例如当前日志等级是 ERROR，则只会记录 ERROR 级别的日志，DEBUG、INFO 和 WARNING 级别的日志都不会被记录
    # DEBUG < INFO < WARNING < ERROR

    logger.info(f"日志器初始化... 日志文件 {log_file} 当前日志等级 {level}")
    logger.info(
        f"日志器配置：轮转大小 {ROTATION_SIZE}，保留天数 {5} 天，旧日志压缩为 zip 格式"
    )
