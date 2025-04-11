"""
Google Cloud 服务客户端管理模块
提供懒加载的客户端实例
"""
from functools import lru_cache
import time
import logging

logger = logging.getLogger(__name__)

# 客户端实例缓存
_speech_client = None
_translate_client = None

def get_speech_client():
    """
    懒加载方式获取 Speech-to-Text 客户端
    """
    global _speech_client
    if _speech_client is None:
        logger.info("初始化 Speech-to-Text 客户端...")
        start_time = time.time()
        from google.cloud import speech_v1p1beta1 as speech
        _speech_client = speech.SpeechClient()
        logger.info(f"Speech-to-Text 客户端初始化完成，耗时: {time.time() - start_time:.2f}秒")
    return _speech_client

def get_translate_client():
    """
    懒加载方式获取 Translate 客户端
    """
    global _translate_client
    if _translate_client is None:
        logger.info("初始化 Translate 客户端...")
        start_time = time.time()
        from google.cloud import translate_v2 as translate
        _translate_client = translate.Client()
        logger.info(f"Translate 客户端初始化完成，耗时: {time.time() - start_time:.2f}秒")
    return _translate_client