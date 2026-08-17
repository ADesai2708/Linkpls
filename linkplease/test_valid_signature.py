import hashlib
import hmac
import json

import requests

from app.database import settings


url = "http://127.0.0.1:8000/webhook"


payload = {
    "event_id": "evt_valid_hmac_002",
    "event_type": "comment.created",
    "sent_at": "2026-08-17T08:40:00Z",
    "data": {
        "comment_id": "cmt_valid_hmac_002",
        "post_id": "post_valid_hmac_002",
        "text": "PRICE please",
        "created_at": "2026-08-17T08:39:59Z",
        "from": {
            "user_id": "usr_valid_hmac_002",
            "username": "valid_hmac_user"
        }
    }
}


# Create the exact bytes that will be sent.
raw_body = json.dumps(
    payload,
    separators=(",", ":")
).encode("utf-8")
print(
    "CLIENT body fingerprint:",
    hashlib.sha256(raw_body).hexdigest()[:12]
)

print(
    "CLIENT key fingerprint:",
    hashlib.sha256(
        settings.pseudogram_api_key.encode()
    ).hexdigest()[:12]
)

# Sign those exact bytes.
signature = hmac.new(
    settings.pseudogram_api_key.encode("utf-8"),
    raw_body,
    hashlib.sha256
).hexdigest()


headers = {
    "Content-Type": "application/json",
    "X-PseudoGram-Signature": f"sha256={signature}",
}


print("SIGNATURE:", f"sha256={signature}")
print("BODY:", raw_body.decode())


response = requests.post(
    url,
    json=payload,
    headers=headers,
)


print("STATUS:", response.status_code)
print("RESPONSE:", response.text)