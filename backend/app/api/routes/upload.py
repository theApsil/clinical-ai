import json
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.parser import PDFParser
from app.services.chunker import TextChunker
from app.services.guideline_aggregator import GuidelineAggregator
from app.services.llm_client import LLMClient
from app.services.dialog_manager import DialogManager
from app.api.deps import create_session

router = APIRouter(prefix="/upload", tags=["upload"])
BASE_DIR = Path(__file__).resolve().parents[2]
PROMPTS_DIR = BASE_DIR / "prompts"

@router.post("/")
async def upload_guideline(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF supported")

    tmp_path = Path(f"/tmp/{file.filename}")
    tmp_path.write_bytes(await file.read())

    parser = PDFParser()
    text = parser.parse(str(tmp_path))

    chunker = TextChunker()
    chunks = chunker.split(text)

    llm = LLMClient()
    aggregator = GuidelineAggregator()

    prompt = (PROMPTS_DIR / "extract_guideline.txt").read_text(encoding="utf-8")

    for chunk in chunks:
        partial = llm.extract_guideline(chunk, prompt)
        aggregator.add(partial)

    guideline = aggregator.get()

    prompts = {
        "extract_patient_facts": (PROMPTS_DIR / "extract_patient_facts.txt").read_text(encoding="utf-8"),
        "ask_clarifying_questions": (PROMPTS_DIR / "ask_clarifying_questions.txt").read_text(encoding="utf-8"),
        "final_decision": (PROMPTS_DIR / "final_decision.txt").read_text(encoding="utf-8"),
    }

    dialog_manager = DialogManager(
        guideline=guideline,
        prompts=prompts
    )

    session_id = create_session(dialog_manager)

    return {
        "session_id": session_id,
        "message": "Guideline processed successfully"
    }
