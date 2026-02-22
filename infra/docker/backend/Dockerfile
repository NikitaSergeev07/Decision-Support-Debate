FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY agent_debate ./agent_debate

RUN pip install --upgrade pip && \
    pip install . fastapi "uvicorn[standard]" sse-starlette

EXPOSE 8000

CMD ["uvicorn", "agent_debate.api:app", "--host", "0.0.0.0", "--port", "8000"]
