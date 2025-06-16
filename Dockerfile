FROM python:3.12-slim

# ensure stdout/stderr is unbuffered, no .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app and db scripts
COPY app/ ./app
COPY db/ ./db

# default command used by Render (no startCommand in render.yaml)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
