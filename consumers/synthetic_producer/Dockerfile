FROM python:3.12-slim
WORKDIR /app
COPY consumers/synthetic_producer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY consumers/shared/ ./shared/
COPY consumers/synthetic_producer/ ./synthetic_producer/
ENV PYTHONUNBUFFERED=1
CMD ["python", "-m", "synthetic_producer.main"]