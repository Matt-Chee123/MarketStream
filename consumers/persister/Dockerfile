FROM python:3.12-slim
WORKDIR /app

COPY consumers/persister/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY consumers/shared /app/shared
COPY consumers/persister/main.py /app/main.py

CMD ["python", "-u", "main.py"]