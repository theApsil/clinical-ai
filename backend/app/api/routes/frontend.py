from fastapi import APIRouter, Request

from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="", tags=["frontend"])
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@router.get("/status/{task_id}")
async def status_page(request: Request, task_id: str):
    return templates.TemplateResponse("status.html", {"request": request, "task_id": task_id})

@router.get("/chat/{session_id}")
async def chat_page(request: Request, session_id: str):
    return templates.TemplateResponse("chat.html", {"request": request, "session_id": session_id})

