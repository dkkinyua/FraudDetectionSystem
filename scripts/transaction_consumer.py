import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StringType, DoubleType, StructType, IntegerType

load_dotenv()

'''
Steps:
Set up KafkaConsumer
Set up SparkSession
Set up transform_data (contains all transactions):
    - Define the schema
        - The data that we want is inside the value dictionary as so: value
        - So define schema
    - Define df using readStream, read data from Kafka topic
    - Parse data into JSON from the value dictionary
    - Run transformations like changing timestamp into a datetime
Set up writing helper function, write_as_batch:
    - Write batches of data into psql database using write.jdbc()
Set up write_to_db:
    shop.transactions holds the fraudulent data without the is_fraud data for downstream use cases
    - Write to db using writeStream() and forEachBatch(write_as_batch)
    - This is where we use the helper function
'''

spark = SparkSession.builder \
                    .appName("FraudConsumer") \
                    .master('local[*]') \
                    .config(
                            "spark.jars.packages",
                            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,"
                            "org.postgresql:postgresql:42.7.7"
                        )\
                    .config("spark.ui.port", "4040") \
                    .getOrCreate()

def transform_data():
    schema = StructType() \
                    .add('user_id', StringType()) \
                    .add('transaction_id', StringType()) \
                    .add('timestamp', StringType()) \
                    .add('first_name', StringType()) \
                    .add('last_name', StringType()) \
                    .add('full_name', StringType()) \
                    .add('email', StringType()) \
                    .add('location', StringType()) \
                    .add('transaction_location', StringType()) \
                    .add('amount', DoubleType()) \
                    .add('device', StringType()) 
                        
    df = spark.readStream \
              .format('kafka') \
              .option('kafka.bootstrap.servers', os.getenv("BOOTSTRAP_SERVERS")) \
              .option('subscribe', "transactions-data") \
              .option('startingOffsets', 'earliest') \
              .option('kafka.security.protocol', 'SASL_SSL') \
              .option('kafka.sasl.mechanism', 'SCRAM-SHA-256') \
              .option('kafka.sasl.jaas.config',
                    f'org.apache.kafka.common.security.scram.ScramLoginModule required '
                    f'username="{os.getenv("USERNAME")}" password="{os.getenv("PASSWORD")}";') \
              .load()

    
    # get data from value and parse into JSON
    json_df = df.selectExpr('CAST (value AS STRING) as parsed_json') \
                .select(from_json(col('parsed_json'), schema).alias('data')) \
                .select('data.*')
    
    new_df = json_df.select(
        'user_id',
        'transaction_id',
        'first_name',
        'last_name',
        'full_name',
        'email',
        'location',
        'transaction_location',
        'amount',
        'device',
        col('timestamp').cast('timestamp')
        )

    return new_df

def write_as_batch(batch_df, epoch_id):
    properties = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "driver": "org.postgresql.Driver"
    }

    try:
        batch_df.write \
                .jdbc(url=os.getenv("DB_URL"), table='shop.transactions', mode='append', properties=properties)
    except Exception as e:
        print(f"Error writing batch data: {e}")

def write_to_transactions():
    df = transform_data()
    path = "/tmp/fraud_detection/transactions"
    try:
        return df.writeStream \
          .foreachBatch(write_as_batch) \
          .outputMode('append') \
          .option('checkpointLocation', path) \
          .start() \
          .awaitTermination()
    except Exception as e:
        print(f"Error streaming data to shop.transactions: {e}")

if __name__ == '__main__':
    write_to_transactions()
        
