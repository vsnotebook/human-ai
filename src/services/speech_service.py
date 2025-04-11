from google.cloud import speech_v2 as speech
from google.cloud.speech_v2.types import cloud_speech
import datetime
import uuid

from src.config.language_config import LANGUAGE_CONFIG
from src.core.config import settings
from src.services.audio_factory import AudioServiceFactory
from src.services.user_service import UserService
from src.services.firestore_service import FirestoreService as DBService
# from src.services.mongodb_service import MongoDBService as DBService

class SpeechService:

    @staticmethod
    async def transcribe_by_userid(audio_content: bytes, language_code: str, user_id: str = None, filename: str = None) -> str:
        if not user_id:
            print("用户ID为空")
            raise ValueError("系统错误")

        # 生成唯一的任务ID
        task_id = str(uuid.uuid4())

        # 获取音频时长
        audio_duration = await UserService.get_audio_duration(audio_content)

        # 扣除用户余额
        await UserService.deduct_audio_time(user_id, audio_duration)

        # 记录开始时间
        start_time = datetime.datetime.now()

        # 根据语言选择不同的识别服务
        # 如果是中文，使用阿里云服务
        # 如果是缅甸语，使用谷歌服务
        if language_code.startswith('zh'):
            # speech_service = AudioServiceFactory.get_speech_service(provider="aliyun")
            speech_service = AudioServiceFactory.get_speech_service(provider="azure")
        else:
            # speech_service = AudioServiceFactory.get_speech_service(provider="google")
            speech_service = AudioServiceFactory.get_speech_service(provider="azure")

        # 执行语音识别
        transcription = await speech_service.recognize(audio_content, language_code)

        # 记录结束时间
        end_time = datetime.datetime.now()
        process_time = (end_time - start_time).total_seconds()

        # 将使用记录保存到数据库
        usage_record = {
            "task_id": task_id,
            "user_id": user_id,
            "task_type": "asr",  # 语音识别
            "language_code": language_code,
            "file_name": filename,
            "audio_duration": audio_duration,
            "process_time": process_time,
            "text_length": len(transcription),
            "file_size": len(audio_content),
            "created_at": start_time,
            "completed_at": end_time,
            "status": "completed"
        }

        # 插入记录到数据库
        DBService.insert_usage_records(usage_record)

        return transcription

    @staticmethod
    async def transcribe(audio_content: bytes, language_code: str) -> str:
        # 获取语言对应的区域
        language_settings = LANGUAGE_CONFIG.get(language_code)

        language_code = language_settings['language_code']
        region = language_settings['region']
        model = language_settings['model']

        client_options = {"api_endpoint": f"{region}-speech.googleapis.com"}
        speech_client = speech.SpeechClient(client_options=client_options)

        config = cloud_speech.RecognitionConfig(
            auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
            language_codes=[language_code],
            model=model,
            features=cloud_speech.RecognitionFeatures(
                enable_automatic_punctuation=True,  # 自动添加标点
            )
        )

        request = cloud_speech.RecognizeRequest(
            recognizer=f"projects/{settings.PROJECT_ID}/locations/{region}/recognizers/_",
            config=config,
            content=audio_content,
        )

        response = speech_client.recognize(request=request)

        transcription = ""
        for result in response.results:
            for alternative in result.alternatives:
                transcription += alternative.transcript

        return transcription
