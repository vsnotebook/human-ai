import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware  # 添加这行
from starlette.middleware.sessions import SessionMiddleware
from src.api.speech import router as speech_router
from src.api.user import router as user_router
from src.api.payment import router as payment_router  # 添加这行
from src.core.config import settings

app = FastAPI()


def check_allowed_origin(origin: str, request: Request) -> bool:
    # 仅当请求路径为 /transcribe 且来源为 http://127.0.0.1:8080 时允许
    # return request.url.path == "/transcribe" and origin == "http://127.0.0.1:8080"
    pass_flag = request.url.path == "/transcribe"
    return pass_flag


# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源，生产环境建议设置具体的域名
    # allow_origins=check_allowed_origin,  # 动态验证源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有请求头
)

# 添加会话支持
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-here",
    session_cookie="session"
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(speech_router)
app.include_router(user_router)
app.include_router(payment_router)  # 添加这行

if __name__ == "__main__":
    uvicorn.run(app, host=settings.SERVER_HOST, port=int(settings.SERVER_PORT))
