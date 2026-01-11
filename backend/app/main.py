from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .api.routes import upload, chat
from .config import settings

app = FastAPI(title=settings.APP_NAME)

app.include_router(upload.router)
app.include_router(chat.router)

app.mount(
    "/",
    StaticFiles(directory="../frontend", html=True),
    name="frontend"
)