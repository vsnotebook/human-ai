import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.core.middleware.timing import timing_middleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from src.api import home, user, admin, auth, profile, payment, translate, voice_translate, interpretation, ws_speech
from src.api.external import asr
from src.core.config import settings
from src.api import demo  # 添加这行

app = FastAPI()

# 添加计时中间件
app.middleware("http")(timing_middleware)


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

# 添加会话中间件
app.add_middleware(
    SessionMiddleware,
    secret_key="d197aa63a2f3caab36c2335e3b0309ef",  # 建议从配置文件读取
    session_cookie="session",
    # max_age=60,  # 会话过期时间，单位为秒（这里设置为1分钟。单位是秒）。默认是2周。
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# 注册路由
app.include_router(auth.router)
app.include_router(home.router)
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(payment.router)
app.include_router(profile.router)
app.include_router(translate.router)
app.include_router(voice_translate.router)
app.include_router(interpretation.router)  # 添加新的路由
app.include_router(demo.router)
app.include_router(asr.router)
app.include_router(ws_speech.router)


if __name__ == "__main__":
    uvicorn.run(app, host=settings.SERVER_HOST, port=int(settings.SERVER_PORT))
