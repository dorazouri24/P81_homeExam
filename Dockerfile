FROM python:3.9-slim-buster

ENV AWS_S3_KEY=s3://p81-performance-test-scenarios/scripts/main.py

WORKDIR /app

COPY requirements.txt .
COPY script.sh /app/
COPY main.py /app/

RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x script.sh
CMD ["sh", "/app/script.sh"]