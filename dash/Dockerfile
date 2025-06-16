FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# install Streamlit + DB driver
COPY dash/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy dashboard code
COPY dash/ ./ 

# default command used by Render
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
