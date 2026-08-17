import json
from urllib import request, error

url = "http://127.0.0.1:8000/webhook"

payload = {
    "event_id": "evt_forged_001",
    "event_type": "comment.created",
    "sent_at": "2026-08-17T08:20:00Z",
    "data": {
        "comment_id": "cmt_forged_001",
        "post_id": "post_forged_001",
        "text": "PRICE please",
        "created_at": "2026-08-17T08:19:59Z",
        "from": {
            "user_id": "usr_forged_001",
            "username": "attacker"
        }
    }
}

headers = {
    "Content-Type": "application/json",
    "X-PseudoGram-Signature": "sha256=definitely_wrong",
}

body = json.dumps(payload).encode("utf-8")
req = request.Request(url, data=body, headers=headers, method="POST")

try:
    with request.urlopen(req) as response:
        print("STATUS:", response.status)
        print("BODY:", response.read().decode("utf-8"))
except error.HTTPError as exc:
    print("STATUS:", exc.code)
    print("BODY:", exc.read().decode("utf-8"))