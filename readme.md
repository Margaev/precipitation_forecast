# Precipitation forecast 

## Prerequisites
* Docker

## How to run:
```shell
docker compose up
```

## Overview
### Components
* Kafka for queuing the messages
* Producer - Python script to simulate API data and produce it to kafka
* Spark Streaming for processing the stream of data from kafka
* PostgreSQL for storing the processing results

### Architecture diagram
![precipitation_forecast.jpg](images%2Fprecipitation_forecast.jpg)

## Useful commands

```shell
docker exec -it -w /opt/bitnami/kafka/bin kafka kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic forecast
```

```shell
./bin/pyspark --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0 --conf spark.driver.extraJavaOptions="-Divy.cache.dir=/tmp -Divy.home=/tmp"
```


