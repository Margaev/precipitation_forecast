import json
import time
from datetime import datetime

from kafka import KafkaProducer

from forecast_simulator import ForecastSimulator


BOOTSTRAP_SERVERS = ["kafka:9092"]
# BOOTSTRAP_SERVERS = ['localhost:9094']


def main():
    """
    main entrypoint
    :return:
    """
    producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)
    print("Producer successfully started")
    forecast_simulator = ForecastSimulator()

    while True:
        print("Sending new message...")
        data = forecast_simulator.get_current_forecast(datetime.now())
        new_msg = bytes(json.dumps(data), encoding="utf-8")
        print(new_msg)

        producer.send("forecast", value=new_msg)
        producer.flush()

        time.sleep(60)


if __name__ == "__main__":
    main()
