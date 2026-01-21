import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from app.logger import logger
from app.services.parser import PDFParser
from app.services.chunker import TextChunker
from app.services.guideline_aggregator import GuidelineAggregator
from app.services.llm_client import LLMClient
from app.services.dialog_manager import DialogManager
from app.api.deps import create_session
from app.services.upload_task import create_task, update_task, get_task
from app.services.yandexclient.YandexLlmClient import YandexLlnClient
router = APIRouter(prefix="/upload", tags=["upload"])
BASE_DIR = Path(__file__).resolve().parents[2]
PROMPTS_DIR = BASE_DIR / "prompts"

@router.post("/")
async def upload_guideline(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    task_id = str(uuid.uuid4())
    create_task(task_id)

    background_tasks.add_task(
        process_guideline,
        task_id,
        file
    )

    return {"task_id": task_id}

def process_guideline(task_id: str, file: UploadFile):
    try:
        update_task(task_id, progress=5)

        tmp_path = Path("/tmp") / file.filename
        tmp_path.write_bytes(file.file.read())

        update_task(task_id, progress=15)

        parser = PDFParser()
        text = parser.parse(str(tmp_path))

        update_task(task_id, progress=30)

        chunker = TextChunker()
        chunks = chunker.split(text)

        update_task(task_id, progress=40)

        llm = YandexLlnClient()
        aggregator = GuidelineAggregator()
        prompt = (PROMPTS_DIR / "extract_guideline.txt").read_text("utf-8")

        step = 50
        step_size = 40 / max(len(chunks), 1)

        for chunk in chunks:
            partial = llm.extract_guideline(chunk, prompt)
            aggregator.add(partial)
            step += step_size
            update_task(task_id, progress=int(step))

        guideline = aggregator.get()

        prompts = {
            "extract_patient_facts": (PROMPTS_DIR / "extract_patient_facts.txt").read_text("utf-8"),
            "ask_clarifying_questions": (PROMPTS_DIR / "ask_clarifying_questions.txt").read_text("utf-8"),
            "final_decision": (PROMPTS_DIR / "final_decision.txt").read_text("utf-8"),
        }

        dialog = DialogManager(guideline, prompts)
        session_id = create_session(dialog)

        update_task(
            task_id,
            status="done",
            progress=100,
            session_id=session_id
        )

    except Exception as e:
        update_task(
            task_id,
            status="error",
            error=str(e)
        )

@router.get("/status/{task_id}")
def upload_status(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task