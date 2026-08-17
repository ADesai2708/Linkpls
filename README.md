LinkPlease 

GITLINK->(https://github.com/ADesai2708/Linkpls.git)

LinkPlease is a small backend service that watches incoming social-media
comments and automates replies through direct messages.

The main idea is simple:

Receive a comment webhook.

Verify that the webhook came from the expected source.

Store the event.

Match the comment against configured rules.

Queue a DM when a rule matches.

Send the DM through the PseudoGram API.

Keep track of delivery status and retries.

The project is built as a FastAPI application with PostgreSQL and a
background worker.

Tech stack

Python 3.12

FastAPI

SQLAlchemy

PostgreSQL

Pydantic / pydantic-settings

HTTPX

Docker

Render

Project structure

linkplease/
├── app/
│   ├── models/
│   │   ├── comment_state.py
│   │   ├── delivery.py
│   │   ├── event.py
│   │   └── rule.py
│   ├── routes/
│   │   ├── rules.py
│   │   ├── stats.py
│   │   └── webhook.py
│   ├── schemas/
│   │   ├── rule.py
│   │   └── webhook.py
│   ├── services/
│   │   ├── delivery_worker.py
│   │   ├── event_processor.py
│   │   ├── event_worker.py
│   │   ├── pseudogram.py
│   │   ├── rate_limiter.py
│   │   └── reconciliation.py
│   ├── database.py
│   └── main.py
├── tests/
├── worker.py
├── Dockerfile
├── render.yaml
├── requirements.txt
└── .gitignore

How it works

Webhook

POST /webhook receives comment events.

The request body is read as raw bytes and verified using an HMAC SHA-256
signature before the JSON payload is processed.

The webhook also handles repeated event IDs so the same event is not
processed twice.

Event processing

Accepted events are stored in PostgreSQL. The worker periodically looks
for pending events and processes them.

For comment.created events, the comment state is created or updated.
Deleted comments are marked as deleted and are not resurrected by a
later create event.

Rules

Rules are stored in the database and are used to decide whether a
comment should trigger a DM.

A matching comment can create a delivery record for the user.

Delivery

PseudoGramClient is responsible for communicating with the PseudoGram
API.

The delivery flow includes:

idempotency keys

delivery status tracking

retry handling

reconciliation of pending deliveries

Rate limiting

A rate limiter is included to prevent the delivery worker from sending
requests without respecting the configured limits.

Background worker

The worker is started with:

python worker.py

It continuously runs:

process_pending_events()
process_queued_deliveries()
reconcile_deliveries()

The Docker deployment currently starts both the worker and FastAPI
server in the same container.

Running locally

Create a .env file with the required settings:

DATABASE_URL=your_database_url
PSEUDOGRAM_BASE_URL=your_pseudogram_url
PSEUDOGRAM_API_KEY=your_api_key

Do not commit .env.

Install dependencies:

pip install -r requirements.txt

Start the API:

uvicorn app.main:app --reload

Start the worker in another terminal:

python worker.py

Health check:

GET /health

Docker

The application has been containerized with Python 3.12 slim.

Build:

docker build -t linkplease .

Run locally:

docker run --rm -p 8000:8000 --env-file .env -e PORT=8000 linkplease

The container starts both the worker and the FastAPI server.

Deployment

The application is deployed on Render using the Dockerfile and
render.yaml.

The deployment includes:

a web service

a PostgreSQL database

environment configuration for the PseudoGram API

a health check at /health

Live deployed API:

https://linkplease-dkqe.onrender.com

Health check:

https://linkplease-dkqe.onrender.com/health

The deployed API is publicly accessible at:

https://linkplease-dkqe.onrender.com

## Deployment Screenshots

### Render deployment

The application is deployed on Render and is currently live.

![Render deployment](linkplease\screenshots\Screenshot 2026-08-17 183757.png)

### Worker and API logs

The Render logs confirm that both the background worker and FastAPI server started successfully.

![Worker logs](linkplease\screenshots\Screenshot 2026-08-17 194720.png)

### Health check

The deployed `/health` endpoint confirms that the API is running and connected to PostgreSQL.

![Health check]
(linkplease\screenshots\Screenshot 2026-08-17 194449.png)
### Event processing

A production webhook event was successfully processed.

![Event processed](linkplease\screenshots\Screenshot 2026-08-17 194648.png)

### DM delivery

A matching rule resulted in a successful PseudoGram DM delivery.

![Delivery success](screenshots/delivery-success.png)(![Database](<linkplease/screenshots/Screenshot 2026-08-17 194600.png>))

### Tests

The rate limiter test passes successfully.

![Pytest result](linkplease\screenshots\Screenshot 2026-08-17 194523.png)
The Render service and database were successfully created, and the web
service is currently live.

What has been tested

The following parts were tested successfully:

FastAPI application starts correctly.

PostgreSQL connection works.

Docker image builds successfully.

Docker container starts successfully.

Render deployment succeeds.

Render health check returns 200 OK.

The background worker starts on Render.

HMAC signature verification works with a correctly generated
signature.

A valid webhook was accepted by the deployed API.

The event was processed by the worker.

A matching rule resulted in a DM delivery.

The delivery was confirmed as delivered.

The successful production delivery had one attempt and a PseudoGram
DM ID.

Rate limiter test passes with pytest.

Example production result:

event:
evt_valid_hmac_002

processing_status:
processed

comment:
cmt_valid_hmac_002

delivery:
delivered

attempts:
1

dm_id:
dm_8e2cbe978f54

last_error:
empty

What is not fully verified

There is one thing that was not fully verified before submission: the
final production test for user/rule-level duplicate blocking.

The project contains duplicate-blocking logic, but the last production
test was not completed cleanly.

There was also an earlier local HMAC testing issue caused by the exact
bytes being signed versus the bytes sent in the HTTP request. The
signature verification function itself was tested directly and returned
True for a correctly generated signature, and a valid production
webhook was successfully processed later.

Because the main production flow is already working, no further changes
were made to the application just to force this final test.

Current status

Working

Webhook API

HMAC verification

Event storage

Event processing

Comment state handling

Rule matching

Delivery queue

PseudoGram DM integration

Delivery status tracking

Retry/reconciliation services

Rate limiting

Docker deployment

Render deployment

PostgreSQL

Health check

Background worker

Production DM delivery

Not fully verified

Final production duplicate-blocking scenario

Full production test of every possible retry/failure path

Useful endpoints

GET  /
GET  /health
POST /webhook

