from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response, JSONResponse
import requests

app = FastAPI()

registry = BackendRegistry()
strategy = RoundRobinStrategy()
forwarder = RequestForwarder()
health_checker = HealthChecker(registry)


@app.on_event("startup")
def startup_event():
    registry.register(BackendServer("svc1", "127.0.0.1", 9001))
    registry.register(BackendServer("svc2", "127.0.0.1", 9002))
    registry.register(BackendServer("svc3", "127.0.0.1", 9003))
    health_checker.start()


@app.on_event("shutdown")
def shutdown_event():
    health_checker.stop()


@app.get("/health")
def lb_health():
    return {"status": "ok"}


@app.get("/admin/backends")
def list_backends():
    return [
        {
            "id": b.server_id,
            "host": b.host,
            "port": b.port,
            "healthy": b.healthy,
            "active_connections": b.active_connections,
        }
        for b in registry.get_all()
    ]


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(path: str, request: Request):
    healthy_backends = registry.get_healthy()
    if not healthy_backends:
        raise HTTPException(status_code=503, detail="No healthy backends")

    backend = strategy.select(healthy_backends)
    registry.increment_connections(backend.server_id)

    try:
        body = await request.body()
        response = forwarder.forward(
            backend=backend,
            method=request.method,
            path="/" + path,
            headers=dict(request.headers),
            body=body,
            query_string=request.scope.get("query_string", b""),
        )

        excluded_headers = {"content-encoding", "transfer-encoding", "connection"}
        response_headers = {
            k: v for k, v in response.headers.items()
            if k.lower() not in excluded_headers
        }

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=response_headers,
        )

    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Backend request failed: {str(exc)}")
    finally:
        registry.decrement_connections(backend.server_id)