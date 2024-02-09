from pyspark.sql import SparkSession, Window, DataFrame
from pyspark.sql import functions as f
from pyspark.sql.types import (
    StructType,
    StructField,
    FloatType,
    StringType,
    IntegerType,
    ArrayType,
    TimestampType,
)


class Processor:
    MESSAGE_SCHEMA = StructType(
        [
            StructField("lat", FloatType()),
            StructField("lon", FloatType()),
            StructField("timezone", StringType()),
            StructField("timezone_offset", IntegerType()),
            StructField(
                "minutely",
                ArrayType(
                    StructType(
                        [
                            StructField("dt", TimestampType()),
                            StructField("precipitation", FloatType()),
                        ]
                    )
                ),
            ),
        ]
    )

    def __init__(
        self,
        kafka_host: str,
        kafka_port: str,
        topic: str,
        postgres_url: str,
        postgres_table: str,
        postgres_user: str,
        postgres_password: str,
        watermark_delay_threshold: str = "10 minutes",
        window_duration: str = "60 minutes",
        window_slide_duration: str = "1 minute",
    ):
        self.spark = SparkSession.builder.getOrCreate()
        self.sc = self.spark.sparkContext

        self.kafka_host = kafka_host
        self.kafka_port = kafka_port
        self.topic = topic

        self.postgres_url = postgres_url
        self.postgres_table = postgres_table
        self.postgres_user = postgres_user
        self.postgres_password = postgres_password

        self.watermark_delay_threshold = watermark_delay_threshold
        self.window_duration = window_duration
        self.window_slide_duration = window_slide_duration

    def _read_stream(self) -> DataFrame:
        return (
            self.spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", f"{self.kafka_host}:{self.kafka_port}")
            .option("subscribe", self.topic)
            .load()
        )

    def _preprocess(self, dataframe: DataFrame) -> DataFrame:
        df_decoded = dataframe.withColumn("decoded", f.decode(f.col("value"), "utf-8"))
        df_parsed = df_decoded.withColumn(
            "json",
            f.from_json(f.col("decoded"), schema=self.MESSAGE_SCHEMA),
        )
        df_unpacked = (
            df_parsed.withColumn("lat", f.col("json.lat"))
            .withColumn("lon", f.col("json.lon"))
            .withColumn("timezone", f.col("json.timezone"))
            .withColumn("timezone_offset", f.col("json.timezone_offset"))
            .withColumn("minutely", f.explode(f.col("json.minutely")).alias("minutely"))
        )
        return df_unpacked.select(
            "lat",
            "lon",
            "timezone",
            "timezone_offset",
            f.col("timestamp").alias("kafka_msg_ts"),
            f.col("minutely.dt").alias("dt"),
            f.col("minutely.precipitation").alias("precipitation"),
        )

    def _aggregate(self, dataframe: DataFrame) -> DataFrame:
        return (
            dataframe.withWatermark("dt", self.watermark_delay_threshold)
            .dropDuplicates(["dt"])
            .groupBy(
                f.window(f.col("dt"), self.window_duration, self.window_slide_duration)
            )
            .agg(f.sum("precipitation").alias("precipitation_hour_sum"))
        )

    def _write_jdbc(self, dataframe: DataFrame, epoch_id):
        (
            dataframe.write.mode("append")
            .format("jdbc")
            .option("driver", "org.postgresql.Driver")
            .option("url", self.postgres_url)
            .option("dbtable", self.postgres_table)
            .option("user", self.postgres_user)
            .option("password", self.postgres_password)
            .save()
        )

    def _write_stream(self, dataframe):
        query = (
            dataframe.select(
                f.col("window.start"),
                f.col("window.end"),
                f.col("precipitation_hour_sum"),
            )
            .writeStream.outputMode("append")
            .foreachBatch(self._write_jdbc)
            .start()
        )
        query.awaitTermination()

    def run(self):
        df = self._read_stream()
        df.printSchema()
        preprocessed_df = self._preprocess(df)
        aggregated_df = self._aggregate(preprocessed_df)
        aggregated_df.printSchema()
        self._write_stream(aggregated_df)


if __name__ == "__main__":
    processor = Processor(
        kafka_host="kafka",
        kafka_port="9092",
        topic="forecast",
        postgres_url="jdbc:postgresql://postgres/precipitation_forecast",
        postgres_table="precipitation_sum",
        postgres_user="username",
        postgres_password="password",
    )
    processor.run()
