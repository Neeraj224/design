from dataclasses import dataclass, field
from threading import Lock
import time

@dataclass
class BackendServer:
    server_id: str
    host: str
    port: int
    healthy: bool = True
    active_connections: int = 0
    last_health_check_ts: float = field(default_factory = time.time)

    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"