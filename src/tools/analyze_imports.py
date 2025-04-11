import time
import importlib
import logging
import sys

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def measure_import_time(module_name):
    """测量导入单个模块的时间"""
    start = time.time()
    try:
        importlib.import_module(module_name)
        end = time.time()
        return end - start, None
    except Exception as e:
        return 0, str(e)

def analyze_imports():
    """分析主要模块的导入时间"""
    # 主要模块列表 - 根据main_web.py中的导入调整
    modules = [
        "fastapi",
        "uvicorn",
        "src.core.middleware.timing",
        "fastapi.staticfiles",
        "starlette.middleware.sessions",
        "src.api.home",
        "src.api.user",
        "src.api.admin", 
        "src.api.auth",
        "src.api.profile",
        "src.api.payment",
        "src.api.translate",
        "src.api.voice_translate",
        "src.api.interpretation",
        "src.api.ws_speech",
        "src.api.external.asr",
        "src.core.config",
        "src.api.demo",
    ]
    
    results = []
    for module in modules:
        time_taken, error = measure_import_time(module)
        if error:
            logger.error(f"导入 {module} 失败: {error}")
        else:
            results.append((module, time_taken))
            logger.info(f"导入 {module} 耗时: {time_taken:.4f}秒")
    
    # 按耗时排序
    results.sort(key=lambda x: x[1], reverse=True)
    
    logger.info("\n===== 模块导入时间排序 =====")
    for module, time_taken in results:
        logger.info(f"{module}: {time_taken:.4f}秒")

if __name__ == "__main__":
    logger.info("开始分析模块导入时间...")
    analyze_imports()
    logger.info("分析完成")