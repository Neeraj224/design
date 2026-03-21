from fastapi import FastAPI
from fastapi.responses import JSONResponse
import os
import socket
import time

app = FastAPI()

SERVICE_NAME = os.getenv("SERVICE_NAME", "backend")
PORT = os.getenv("PORT", "9001")


@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/work")
def work():
    return {
        "service": SERVICE_NAME,
        "hostname": socket.gethostname(),
        "timestamp": time.time(),
        "message": "Request served successfully",
    }


@app.get("/{path:path}")
def catch_all(path: str):
    return {
        "service": SERVICE_NAME,
        "path": path,
        "message": "Handled by backend",
    }