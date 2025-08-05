import random
import uuid
from datetime import datetime
from faker import Faker

faker = Faker()

Faker.seed(10)
random.seed(10)
NUM_USERS = 500
NUM_TRANSACTIONS = 2500
FRAUD_PCT = 0.08 

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
        'location': location
    })

def generate_transaction_data(user, is_fraud=False):
    transaction_id = str(uuid.uuid4())
    timestamp = faker.date_time_between(start_date='-1d', end_date='now')
    base_location = user['location'] # normal location for this user

    # logic if the transaction is fraudelent, if not, the else block executes
    if is_fraud:
        fraud_type = random.choice(['high_amount', 'unknown_device', 'location_change'])
        transaction_location = faker.country() if fraud_type == 'location_change' else base_location
        amount = round(random.uniform(2000, 15000), 2) if fraud_type == 'high_amount' else round(random.uniform(10, 500), 2)
        device = random.choice(['Tor Browser', 'Microwave', 'Smart Fridge', 'Smart Fridge', 'Unknown Device']) if fraud_type == 'unknown_device' else random.choice(['Mobile', 'Desktop', 'Tablet'])
        fraud_label = 1

    else:
        transaction_location = base_location
        amount = round(random.uniform(10, 500), 2)
        device = random.choice(['Mobile', 'Desktop', 'Tablet'])
        fraud_label = 0

    
    transactions.append({
        'user_id': user['user_id'],
        'transaction_id': transaction_id,
        'first_name': user['first_name'],
        'last_name': user['last_name'],
        'full_name': user['full_name'],
        'location': user['location'],
        'transaction_location': transaction_location,
        'amount': amount,
        'device': device,
        'is_fraud': fraud_label
    })

if __name__ == '__main__':
    transactions = []
    for _ in range(NUM_TRANSACTIONS):
        user = random.choice(users)
        is_fraud = random.random() < FRAUD_PCT
        tx = generate_transaction_data(user, is_fraud)
        transactions.append(tx)

    print(transactions[0:5])


