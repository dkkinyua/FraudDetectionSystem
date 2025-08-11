FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
openjdk-17-jre-headless \
curl \
gnupg \
apt-transport-https \
ca-certificates && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

COPY . /app/

WORKDIR /app

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1 \
    PORT=8000

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]