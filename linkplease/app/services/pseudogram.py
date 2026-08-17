from typing import Any

import httpx

from app.database import settings


class PseudoGramClient:

    def __init__(self):
        self.base_url = settings.pseudogram_base_url
        self.api_key = settings.pseudogram_api_key

    def _headers(self) -> dict[str, str]:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def send_dm(
        self,
        recipient_user_id: str,
        message: str,
        comment_id: str,
        idempotency_key: str,
    ):
        url = f"{self.base_url}/v1/dm/send"

        payload = {
            "recipient_user_id": recipient_user_id,
            "message": message,
            "comment_id": comment_id,
        }

        headers = self._headers()
        headers["Idempotency-Key"] = idempotency_key

        response = httpx.post(
            url,
            json=payload,
            headers=headers,
            timeout=10.0,
        )

        
        try:
            body = response.json()
        except ValueError:
            body = {}

        return response.status_code, body, dict(response.headers)

    def get_dm_status(
        self,
        dm_id: str,
    ) -> dict[str, Any]:

        url = f"{self.base_url}/v1/dm/{dm_id}"

        response = httpx.get(
            url,
            headers=self._headers(),
            timeout=10.0,
        )

        response.raise_for_status()

        return response.json()