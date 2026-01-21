import json
from pathlib import Path

from app.services.parser import PDFParser
from app.services.chunker import TextChunker
from app.services.guideline_aggregator import GuidelineAggregator
from app.services.llm_client import LLMClient
from app.services.yandexclient.YandexLlmClient import YandexLlmClient


PROMPT_PATH = Path("../prompts/extract_guideline.txt")


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def main(pdf_path: str):
    print("=== TEST GUIDELINE PIPELINE ===")

    print("[1] Parsing PDF...")
    parser = PDFParser()
    text = parser.parse(pdf_path)
    print(f"    Parsed text length: {len(text)} chars")

    print("[2] Chunking text...")
    chunker = TextChunker(max_chunk_size=3500)
    chunks = chunker.split(text)
    print(f"    Total chunks: {len(chunks)}")

    print("[3] Extracting guideline structure...")
    llm = LLMClient()
    ya = YandexLlmClient()
    aggregator = GuidelineAggregator()
    prompt_template = load_prompt()

    for idx, chunk in enumerate(chunks, start=1):
        print(f"    → Processing chunk {idx}/{len(chunks)}")
        try:
            partial = ya.extract_guideline(
                text=chunk,
                prompt=prompt_template
            )
            aggregator.add(partial)
        except Exception as e:
            print(f"    ❌ Error on chunk {idx}: {e}")

    guideline = aggregator.get()

    print("[4] Final aggregated guideline:")
    print(json.dumps(guideline, ensure_ascii=False, indent=2))

    out_path = Path("guideline_result.json")
    out_path.write_text(
        json.dumps(guideline, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"[✓] Saved to {out_path.resolve()}")


if __name__ == "__main__":
    main("test.pdf")
