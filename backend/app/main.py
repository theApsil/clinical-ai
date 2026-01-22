# Clinical AI
# Copyright (c) 2026 Гончарук Данил Максимович
# All rights reserved.
# Unauthorized copying, modification, or use is prohibited.
# See LICENSE file for details.

from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from .api.routes import upload, chat, healthcheck, frontend
from .config import settings




def create_app():
    app = FastAPI(
        title=settings.APP_NAME,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    app.include_router(upload.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")
    app.include_router(healthcheck.router)
    app.include_router(frontend.router)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/api/v1/openapi.json", include_in_schema=False)
    async def custom_openapi():
        if app.openapi_schema is None:
            app.openapi_schema = get_openapi(
                title=app.title,
                version=app.version,
                routes=app.routes,
            )
        return JSONResponse(app.openapi_schema)

    # Эндпоинт для Swagger UI
    @app.get("/api/v1/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/api/v1/openapi.json",
            title=app.title + " - Swagger UI",
            swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",  # опционально
        )

    # Опционально: ReDoc
    @app.get("/api/v1/redoc", include_in_schema=False)
    async def custom_redoc_html():
        from fastapi.openapi.docs import get_redoc_html
        return get_redoc_html(
            openapi_url="/api/v1/openapi.json",
            title=app.title + " - ReDoc",
        )

    return app