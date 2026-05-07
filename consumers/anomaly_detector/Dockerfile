FROM python:3.12-slim
WORKDIR /app
COPY consumers/anomaly_detector/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY consumers/shared /app/shared
COPY consumers/anomaly_detector/main.py /app/main.py
CMD ["python", "-u", "main.py"]