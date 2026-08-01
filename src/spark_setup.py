from pyspark.sql import SparkSession
# Import tool for clean jupyter
from IPython.display import clear_output
import yaml


def get_spark_session(config_path: str = "spark_config.yaml") -> SparkSession:

      with open(config_path, "r") as f:
          cfg = yaml.safe_load(f)["spark"]

      spark_session = SparkSession.builder \
            .appName(cfg["app_name"]) \
            .config("spark.jars.packages", cfg["jars"]["packages"]) \
            .config("spark.sql.extensions", cfg["sql"]["extensions"]) \
            .config("spark.sql.catalog.local", cfg["catalog"]["local"]["class"]) \
            .config("spark.sql.catalog.local.type", cfg["catalog"]["local"]["type"]) \
            .config("spark.sql.catalog.local.warehouse", cfg["catalog"]["local"]["warehouse"]) \
            .config("spark.ui.enabled", cfg["ui_enabled"]) \
            .getOrCreate()
      
      spark_session.sparkContext.setLogLevel("ERROR")
      spark_session.sql("USE local")
      
      return spark_session