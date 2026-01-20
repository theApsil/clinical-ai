# Clinical AI
# Copyright (c) 2026 Гончарук Данил Максимович
# All rights reserved.
# Unauthorized copying, modification, or use is prohibited.
# See LICENSE file for details.

import uvicorn
from app.main import create_app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True, workers=1, log_config=None
    )
