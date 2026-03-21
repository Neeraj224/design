import threading
import requests
import time

class HealthChecker:
    def __init__(self, registry: BackendRegistry, interval_sec: int = 5, timeout_sec: int = 2):
        self._registry = registry
        self._interval_sec = interval_sec
        self._timeout_sec = timeout_sec
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._thread.join(timeout=2)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            backends = self._registry.get_all()
            for backend in backends:
                try:
                    resp = requests.get(
                        f"{backend.base_url()}/health",
                        timeout=self._timeout_sec,
                    )
                    self._registry.mark_health(backend.server_id, resp.status_code == 200)
                except requests.RequestException:
                    self._registry.mark_health(backend.server_id, False)

            time.sleep(self._interval_sec)