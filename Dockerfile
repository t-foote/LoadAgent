# syntax=docker/dockerfile:1

FROM python:3.12-slim AS base

# Prevents Python from writing .pyc files and enables stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=10000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python deps layer 
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Application source
COPY ./app ./app
COPY ./db ./db

# Expose & launch
EXPOSE ${PORT}

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
