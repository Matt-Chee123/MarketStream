FROM python:3.12-slim
WORKDIR /app
COPY consumers/feature_processor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY consumers/shared /app/shared
COPY consumers/feature_processor/main.py /app/main.py
CMD ["python", "-u", "main.py"]