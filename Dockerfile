FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    HOST=0.0.0.0 \
    PORT=8000 \
    DATA_ROOT=/app/data

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY requirements.txt ./requirements.txt
COPY web/backend/requirements.txt ./web-backend-requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt -r web-backend-requirements.txt

COPY src ./src
COPY web/__init__.py ./web/__init__.py
COPY web/backend ./web/backend

RUN mkdir -p /app/data/runs /app/data/environments

EXPOSE 8000

CMD ["sh", "-c", "uvicorn web.backend.app:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}"]
