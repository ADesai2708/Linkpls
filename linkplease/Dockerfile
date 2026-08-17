FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "echo '=== STARTING LINKPLEASE WORKER ===' && python worker.py & echo '=== STARTING LINKPLEASE API ===' && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]