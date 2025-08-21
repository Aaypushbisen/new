FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8080

CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:${PORT:-8080}", "app.app:app"]

