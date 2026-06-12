import json
import time
import requests

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

API_KEY = "cf676f5be03a469185844423262905"

CITY = "Chennai"

URL = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}&aqi=no"

while True:

    try:

        producer = KafkaProducer(

            bootstrap_servers=['kafka:9092'],

            value_serializer=lambda v:
            json.dumps(v).encode('utf-8')

        )

        print("Producer connected to Kafka!")

        break

    except NoBrokersAvailable:

        print("Kafka not ready for producer, retrying...")

        time.sleep(5)

while True:

    try:

        response = requests.get(URL)

        data = response.json()

        producer.send('weather', value=data)

        producer.flush()

        print("Sent Weather Data:", data["current"]["temp_c"])

        time.sleep(10)

    except Exception as e:

        print("Producer error:", e)