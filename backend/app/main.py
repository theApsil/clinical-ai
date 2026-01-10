from fastapi import FastAPI

from app.api.routes import upload, chat
from app.config import settings

app = FastAPI(title=settings.APP_NAME)

app.include_router(upload.router)
app.include_router(chat.router)
