import uvicorn
from app.main import create_app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True, workers=5, log_config=None
    )
