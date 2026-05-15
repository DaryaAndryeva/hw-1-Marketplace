"""API Gateway — точка входа маркетплейса.

ДЗ-1: сервис не содержит бизнес-логики. Его роль — продемонстрировать,
что компонент с C4-диаграммы поднимается в Docker и отдаёт 200 OK
на health-check эндпоинт.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

SERVICE_NAME = "api-gateway"
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "0.1.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

STARTED_AT = datetime.now(timezone.utc)


app = FastAPI(
    title="Marketplace API Gateway",
    version=SERVICE_VERSION,
    description=(
        "Единая точка входа в маркетплейс. "
        "На этом этапе ДЗ сервис не реализует бизнес-логику — "
        "только health/readiness эндпоинты, требуемые заданием."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


@app.get("/", tags=["meta"], summary="Метаинформация о сервисе")
def root() -> dict:
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "environment": ENVIRONMENT,
        "started_at": STARTED_AT.isoformat(),
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
    }


@app.get(
    "/health",
    tags=["infra"],
    summary="Liveness probe",
    status_code=status.HTTP_200_OK,
)
def health() -> JSONResponse:
    """Возвращает 200 OK, пока процесс жив.

    Этот эндпоинт требуется условиями ДЗ-1.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "ok",
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
        },
    )


@app.get(
    "/ready",
    tags=["infra"],
    summary="Readiness probe",
    status_code=status.HTTP_200_OK,
)
def ready() -> JSONResponse:
    """Готовность принимать трафик.

    В реальном gateway здесь проверялись бы upstream-сервисы (Identity,
    Catalog и т.д.). В рамках ДЗ их нет, поэтому readiness совпадает
    с liveness — это допустимая упрощённая реализация.
    """
    uptime_seconds = (datetime.now(timezone.utc) - STARTED_AT).total_seconds()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "ready",
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "uptime_seconds": round(uptime_seconds, 3),
        },
    )
