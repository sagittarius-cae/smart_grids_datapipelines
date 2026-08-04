from pyspark.sql import DataFrame, SparkSession

class DataIO:
    def __init__(self, spark_session: SparkSession) -> None:
         self.spark = spark_session

    def read_csv(self, filename: str) -> DataFrame:
        return self.spark_session.read \
             .option("header", "true") \
             .option("inferSchema", "true") \
             .csv("./data_lakehouse/cataglog/{filename}")



    def read_parquet(self, delta_table_name: str) -> None:
        return self.spark_session \
            .read.format("iceberg") \
            .load(delta_table_name)



    def write_delta_table(self, df: DataFrame, table_name: str, partitioned_by: list = None, mode: str = "append") -> None:
        self.spark_session.sql("CREATE DATABASE IF NOT EXISTS {table_name}")

        writer = df.writeTo(table_name) \
                   .using("iceberg") \
                   .tableProperty("format-version", "2")

        if partitioned_by:
             writer = writer.partitionedBy(*partitioned_by)

        match mode: 
            case "createOrReplace": 
                writer.createOrReplace()

            case "create":
                writer.create()

            case "append":
                writer.append()

    def read_parquet(self, table_name:str,  format: str = "iceberg") -> DataFrame:
        return self.spark_session.read \
             .format(format) \
             .load(table_name)