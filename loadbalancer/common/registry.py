class BackendRegistry:
    def __init__(self):
        self._backends = {}
        self._lock = Lock()

    def register(self, backend: BackendServer) -> None:
        with self._lock:
            self._backends[backend.server_id] = backend

    def deregister(self, server_id: str) -> None:
        with self._lock:
            self._backends.pop(server_id, None)

    def get_all(self) -> list[BackendServer]:
        with self._lock:
            return list(self._backends.values())

    def get_healthy(self) -> list[BackendServer]:
        with self._lock:
            return [b for b in self._backends.values() if b.healthy]

    def mark_health(self, server_id: str, healthy: bool) -> None:
        with self._lock:
            if server_id in self._backends:
                self._backends[server_id].healthy = healthy
                self._backends[server_id].last_health_check_ts = time.time()

    def increment_connections(self, server_id: str) -> None:
        with self._lock:
            if server_id in self._backends:
                self._backends[server_id].active_connections += 1

    def decrement_connections(self, server_id: str) -> None:
        with self._lock:
            if server_id in self._backends and self._backends[server_id].active_connections > 0:
                self._backends[server_id].active_connections -= 1