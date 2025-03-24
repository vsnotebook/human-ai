import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from api.speech import router as speech_router
from api.user import router as user_router
from env import SERVER_HOST, SERVER_PORT

app = FastAPI()

# 添加会话支持
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-here",  # 请更改为安全的密钥
    session_cookie="session"
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(speech_router)
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)