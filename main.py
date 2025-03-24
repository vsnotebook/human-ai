import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.speech import router
from env import SERVER_HOST, SERVER_PORT

app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)