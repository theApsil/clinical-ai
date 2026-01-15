from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from .api.routes import upload, chat
from .config import settings, BASE_DIR


app = FastAPI(title=settings.APP_NAME)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(upload.router)
app.include_router(chat.router)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/status/{task_id}")
async def status_page(request: Request, task_id: str):
    return templates.TemplateResponse("status.html", {"request": request, "task_id": task_id})

@app.get("/chat/{session_id}")
async def chat_page(request: Request, session_id: str):
    return templates.TemplateResponse("chat.html", {"request": request, "session_id": session_id})