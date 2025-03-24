import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from api.speech import router
from env import SERVER_HOST, SERVER_PORT

app = FastAPI()

# 添加会话支持
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key-here",  # 请更改为安全的密钥
    session_cookie="session"
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)