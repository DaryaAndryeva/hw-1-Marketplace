import os
from datetime import datetime, timezone

from fastapi import FastAPI

VERSION = os.getenv("SERVICE_VERSION", "0.1.0")

app = FastAPI(title="marketplace-gateway", version=VERSION)

_started = datetime.now(timezone.utc)


@app.get("/")
def index():
    return {"service": "api-gateway", "version": VERSION}


@app.get("/health")
def health():
    return {"status": "ok", "service": "api-gateway", "version": VERSION}


@app.get("/ready")
def ready():
    uptime = (datetime.now(timezone.utc) - _started).total_seconds()
    return {"status": "ready", "uptime_seconds": round(uptime, 2)}
