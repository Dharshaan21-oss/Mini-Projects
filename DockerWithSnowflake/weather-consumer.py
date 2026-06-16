import json
import time

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

import snowflake.connector

# ----------------------------
# Kafka Connection
# ----------------------------

while True:

    try:

        consumer = KafkaConsumer(
            'weather',
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda x:
            json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='weather-group'
        )

        print("Connected to Kafka!")

        break

    except NoBrokersAvailable:

        print("Kafka not ready, retrying in 5 seconds...")

        time.sleep(5)

# ----------------------------
# Snowflake Connection
# ----------------------------

while True:

    try:

        conn = snowflake.connector.connect(
            user='',
            password='',
            account='',
            warehouse='COMPUTE_WH',
            database='WEATHERDB',
            schema='WEATHERR'
        )

        cur = conn.cursor()

        print("Connected to Snowflake!")

        break

    except Exception as e:

        print("Snowflake not ready:", e)

        time.sleep(5)

# ----------------------------
# Consume Messages
# ----------------------------

for message in consumer:

    weather = message.value

    try:

        city = weather['location']['name']
        temp = weather['current']['temp_c']
        condition = weather['current']['condition']['text']

        cur.execute(
            """
            INSERT INTO WEATHER_DATA
            (CITY,TEMPERATURE,CONDITION)
            VALUES (%s,%s,%s)
            """,
            (city,temp,condition)
        )

        conn.commit()

        print(
            f"Inserted into Snowflake: "
            f"{city} {temp}°C {condition}"
        )

    except Exception as e:

        print("Insertion Error:", e)