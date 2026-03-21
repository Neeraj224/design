class RequestForwarder:
    HOP_BY_HOP_HEADERS = {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
        "host",
    }

    def forward(self, backend: BackendServer, method: str, path: str, headers: dict, body: bytes, query_string: bytes):
        import requests

        target_url = f"{backend.base_url()}{path}"
        if query_string:
            target_url += f"?{query_string.decode()}"

        forwarded_headers = {
            k: v for k, v in headers.items()
            if k.lower() not in self.HOP_BY_HOP_HEADERS
        }

        response = requests.request(
            method=method,
            url=target_url,
            headers=forwarded_headers,
            data=body,
            timeout=(2, 5),
        )
        return response