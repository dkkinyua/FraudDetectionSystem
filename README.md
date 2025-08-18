# FraudDetectionSystem
## Overview
Real-time fraud detection pipeline for financial transactions using Kafka, Spark Structured Streaming, PostgreSQL, Isolation Forest, Grafana, and Streamlit.

This project simulates transactions, detects anomalies, stores them in a database, and provides both real-time dashboards (Grafana) and machine learning insights (Streamlit).

## Project Features
- Kafka Producer: generates synthetic transactions with fraud flag, `is_fraud`. Learn why synthetic data is mostly used in ML model training as opposed to real data [here](https://mailchimp.com/resources/what-is-synthetic-data/)

- Spark Structured Streaming: two consumers (transaction_consumer & fraud_consumer).

- PostgreSQL sink: stores transactions and flagged frauds.

- Grafana dashboards: real-time monitoring & SQL analytics.

- Isolation Forest ML model: trained offline, saved to `jobs/isolation_forest.pkl`.

- Streamlit app: visualizes model predictions & performance.

- Docker Setup: services run end-to-end with `docker compose up`.

## Project Architecture:
![Project Architecture](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/8jv3t0b4r0nr9k9tk26v.jpg)

## Project Setup
### 1. Clone this repository

```bash
git clone https://github.com/dkkinyua/FraudDetectionSystem.git
cd FraudDetectionSystem
```

### 2. Set up virtual environment and install required dependencies

```bash
python3 -m venv myenv
source myenv/bin/activate # MacOS/ Linux
myenv\Scripts\activate # Windows/Powershell

pip install -r requirements.txt
```

### 3. Run all services in Docker

```bash
docker compose up --build
```

The services include:
- `trainer`: which trains the model when run
- `producer`: invokes the producer to write data in Kafka topic
- `transaction-consumer` and `fraud-consumer`: invokes the consumers to consume and write data to Postgres

### 4. Setup Kafka on Redpanda.

The Apache Kafka used in this project is cloud-based, hosted on Redpanda. Visit their [website](https://cloud.redpanda.com) to start configuring your Kafka cluster and topic free for 15 days with $100 credit.

### 5. Run Streamlit application

```bash
streamlit run app.py
```

This will run on `localhost:8501` and will show the model's performance.

## Dashboards.

To access the Grafana dashboard, please follow this [link](https://deecodes.grafana.net/public-dashboards/ac5cf512ae80435c8bdb1adad4d1a27c)

![Grafana dashboard](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/dk3ea5t3r5wcg3yux21i.png)


![Streamlit](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/gkfc3c8tlxmvrym8xi44.png)


![Streamlit](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/b8svmoqijw7odvltjaej.png)

## Conclusion

I have written a blog about this project, read it [here](https://dev.to/dkkinyua/building-a-fraud-detection-pipeline-using-python-postgresql-apache-kafka-pyspark-grafana-and-10d5)

Do you have any questions or contributions? Please reach out to me in any of my social media platforms or open a PR request.

