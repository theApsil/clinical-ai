from concurrent.futures import ThreadPoolExecutor, as_completed

from app.services.task_registry import TaskStatus
from app.services import task_registry

from app.services.parser import PDFParser
from app.services.chunker import TextChunker
from app.services.guideline_aggregator import GuidelineAggregator
from app.services.chunk_processor import process_chunk
from app.services.prompts import load_prompt


MAX_WORKERS = 3


def process_guideline(task_id: str, pdf_path: str):
    try:
        task_registry.update(task_id, status=TaskStatus.PROCESSING, progress=0)

        # 1️⃣ PDF → text
        text = PDFParser().parse(pdf_path)
        task_registry.update(task_id, progress=10)

        # 2️⃣ Chunking
        chunks = TextChunker().split(text)
        task_registry.update(task_id, progress=20)

        if not chunks:
            raise ValueError("No text chunks extracted")

        # 3️⃣ Parallel LLM extraction
        prompt = load_prompt("extract_guideline.txt")
        aggregator = GuidelineAggregator()

        total = len(chunks)
        completed = 0

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(process_chunk, chunk, prompt)
                for chunk in chunks
            ]

            for future in as_completed(futures):
                partial = future.result()
                aggregator.add(partial)

                completed += 1
                progress = 20 + int(70 * completed / total)
                task_registry.update(task_id, progress=progress)

        # 4️⃣ Done
        task_registry.update(
            task_id,
            status=TaskStatus.DONE,
            progress=100,
            result=aggregator.get()
        )

    except Exception as e:
        task_registry.update(
            task_id,
            status=TaskStatus.ERROR,
            error=str(e)
        )
