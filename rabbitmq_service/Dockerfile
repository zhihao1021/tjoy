FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rabbitmq_service/ ./rabbitmq_service/
COPY model/ ./model/
COPY embedding_service/ ./embedding_service/
COPY snowflake/ ./snowflake/
COPY db.py .
COPY config.py .


ENV PYTHONPATH=/app
CMD ["python", "./rabbitmq_service/receiver.py"]