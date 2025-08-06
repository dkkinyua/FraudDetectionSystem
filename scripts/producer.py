import os
import json
import random
import uuid
import socket
from dotenv import load_dotenv
from faker import Faker
from kafka import KafkaProducer

load_dotenv()

'''
Steps:
Set up KafkaProducer.Producer
Define number of transactions, users, and fraud probability pct
Set up success and error messages helper functions
generate_users: Generate user data from Faker.faker()
generate_transactions: Generate fraudelent and legit data
stream_transactions: Send data to topic in Redpanda using producer.send(topic, key, value in JSON format)
'''

faker = Faker()
producer = KafkaProducer(
  bootstrap_servers=os.getenv("BOOTSTRAP_SERVERS"),
  security_protocol="SASL_SSL",
  sasl_mechanism="SCRAM-SHA-256",
  sasl_plain_username=os.getenv("USERNAME"),
  sasl_plain_password=os.getenv("PASSWORD"),
  value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

Faker.seed(10)
random.seed(10)
NUM_USERS = 500
NUM_TRANSACTIONS = 2500
FRAUD_PCT = 0.08 
hostname = str.encode(socket.gethostname())

# kafka success and error messages
def on_success(metadata):
    print(f"Message delivered to {metadata.topic} at offset {metadata.offset}")

def on_error(e):
    print(f"An error has occurred: {e}")

def generate_users():
    users = []
    for _ in range(NUM_USERS):
        first_name = faker.first_name()
        last_name = faker.last_name()
        email = faker.email()
        location = faker.country()
        user_id = str(uuid.uuid4())
        users.append({
            'user_id': user_id,
            'first_name': first_name,
            'last_name': last_name,
            'full_name': first_name + ' ' + last_name,
            'email': email,
            'location': location
        })
    
    return users

def generate_transaction_data(user, is_fraud=False):
    transaction_id = str(uuid.uuid4())
    timestamp = faker.date_time_between(start_date='-1d', end_date='now')
    base_location = user['location'] # normal location for this user

    # logic if the transaction is fraudelent, if not, the else block executes
    if is_fraud:
        fraud_type = random.choice(['high_amount', 'unknown_device', 'location_change'])
        transaction_location = faker.country() if fraud_type == 'location_change' else base_location
        amount = round(random.uniform(2000, 15000), 2) if fraud_type == 'high_amount' else round(random.uniform(10, 500), 2)
        device = random.choice(['Tor Browser', 'Microwave', 'Smart Watch', 'Smart Fridge', 'Unknown Device']) if fraud_type == 'unknown_device' else random.choice(['Mobile', 'Desktop', 'Tablet'])
        fraud_label = 1

    else:
        transaction_location = base_location
        amount = round(random.uniform(10, 500), 2)
        device = random.choice(['Mobile', 'Desktop', 'Tablet'])
        fraud_label = 0

    
    return ({
        'user_id': user['user_id'],
        'transaction_id': transaction_id,
        'timestamp': timestamp.isoformat(),
        'first_name': user['first_name'],
        'last_name': user['last_name'],
        'full_name': user['full_name'],
        'email': user['email'],
        'location': user['location'],
        'transaction_location': transaction_location,
        'amount': amount,
        'device': device,
        'is_fraud': fraud_label
    })

def stream_transactions():
    users = generate_users()
    for _ in range(NUM_TRANSACTIONS):
        user = random.choice(users)
        is_fraud = random.random() < FRAUD_PCT
        tx = generate_transaction_data(user, is_fraud)
        # send data to kafka topic
        res = producer.send(os.getenv("TOPIC"), key=hostname, value=tx)
        res.add_callback(on_success)
        res.add_errback(on_error)

if __name__ == '__main__':
    try:
        stream_transactions()
    finally:
        print("Flushing all pending messages to topic...")
        producer.flush()
        producer.close()


