import os
import json
from dotenv import load_dotenv
from kafka import KafkaConsumer
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StringType, DoubleType, StructType, IntegerType

'''
Steps:
Set up KafkaConsumer
Set up SparkSession
Set up transform_data:
    - Define the schema
        - The data that we want is inside the value dictionary as so: value.payload 
        - So define first schema, payload schema
        - Second schema is a derivation from value, taking in the payload schema
    - Define df using readStream, read data from Kafka topic
    - Parse data into JSON from the value['payload'] dictionary
    - Run transformations like changing timestamp into a datetime
Set up writing helper function, write_as_batch:
    - Write batches of data into psql database using write.jdbc()
Set up write_to_db:
    - Write to db using writeStream() and forEachBatch(write_as_batch)
    - This is where we use the helper function
'''

spark = SparkSession.builder \
                    .appName("FraudConsumer") \
                    .master('local[*]') \
                    .config(
                        "spark.jars.packages",
                        "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.1,"
                        "org.postgresql:postgresql:42.7.7"
                    ) \
                    .config("spark.ui.port", "4040") \
                    .getOrCreate()

def transform_data():
    payload_schema = StructType() \
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
                    .add('device', StringType()) \
                    .add('is_fraud', IntegerType()) 

    value_schema = StructType() \
                        .add('payload', payload_schema)
                    
    df = spark.readStream \
              .option('kafka') \
              .option('kafka.bootstrap.servers', os.getenv("BOOTSTRAP_SERVERS")) \
              .option('subscribe', os.getenv("TOPIC")) \
              .option('startingOffsets', 'earliest') \
              .option('kafka.security.protocol', 'SASL_SSL') \
              .option("kafka.group.id", "spark_consumer") \
              .option('kafka.sasl.mechanism', 'PLAIN') \
              .option('kafka.sasl.jaas.config', f'org.apache.kafka.common.security.plain.PlainLoginModule required username="{os.getenv("USERNAME")}" password="{os.getenv("PASSWORD")}";') \
              .load()
    
    # get data from value and parse into JSON
    json_df = df.selectExpr('CAST (value AS STRING) as parsed_json') \
                .select(from_json(col('parsed_json'), value_schema).alias('data')) \
                .select('data.payload.*')
    
    new_df = json_df.withColumn('timestamp', col('timestamp').cast('timestamp'))

    return new_df
