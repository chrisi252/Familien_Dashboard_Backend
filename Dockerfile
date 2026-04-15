FROM python:3.14-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app:create_app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

RUN chmod +x entrypoint.sh

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')"]

CMD ["./entrypoint.sh"]
