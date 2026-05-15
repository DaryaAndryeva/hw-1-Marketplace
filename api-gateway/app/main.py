from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="marketplace-api-gateway")


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse(status_code=200, content={"status": "ok"})


@app.get("/")
def root() -> dict:
    return {"service": "api-gateway"}
