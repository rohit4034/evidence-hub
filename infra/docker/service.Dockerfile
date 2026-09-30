FROM python:3.11-slim

ARG SERVICE_MODULE
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SERVICE_MODULE=${SERVICE_MODULE}
ENV PYTHONPATH=/app:/app/packages/schemas

WORKDIR /app

COPY services/requirements.txt /app/services/requirements.txt
RUN pip install --no-cache-dir -r /app/services/requirements.txt

COPY packages /app/packages
COPY services /app/services

EXPOSE 8000
CMD ["sh", "-c", "uvicorn ${SERVICE_MODULE} --host 0.0.0.0 --port 8000"]

