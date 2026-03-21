from abc import ABC, abstractmethod
from threading import Lock

class LoadBalancingStrategy(ABC):
    @abstractmethod
    def select(self, backends: list[BackendServer]) -> BackendServer:
        pass

class RoundRobinStrategy(LoadBalancingStrategy):
    def __init__(self):
        self._index = 0
        self._lock = Lock()

    def select(self, backends: list[BackendServer]) -> BackendServer:
        if not backends:
            raise RuntimeError("No healthy backends available")

        with self._lock:
            backend = backends[self._index % len(backends)]
            self._index += 1
            return backend
        
class LeastConnectionsStrategy(LoadBalancingStrategy):
    def select(self, backends: list[BackendServer]) -> BackendServer:
        if not backends:
            raise RuntimeError("No healthy backends available")
        return min(backends, key=lambda b: b.active_connections)
    
import random

class RandomStrategy(LoadBalancingStrategy):
    def select(self, backends: list[BackendServer]) -> BackendServer:
        if not backends:
            raise RuntimeError("No healthy backends available")
        return random.choice(backends)