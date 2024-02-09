FROM apache/spark-py:v3.4.0
WORKDIR /opt/spark
COPY processor.py ./work-dir
ENTRYPOINT ["./bin/spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.postgresql:postgresql:42.7.1", "--conf", "spark.driver.extraJavaOptions=\"-Divy.cache.dir=/tmp -Divy.home=/tmp\"", "--conf", "spark.jars.ivy=/tmp/.ivy", "./work-dir/processor.py"]
