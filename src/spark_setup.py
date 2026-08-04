from pyspark.sql import SparkSession
from functools import lru_cache
import yaml

#decorate to cache the spark session
@lru_cache(maxsize=1)
def get_spark_session(config_path: str = "spark_config.yml") -> SparkSession:
    # 1. Read YAML file.
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)["spark"]

    # 2. Intialize the constructor based on fixed parameters from YAML file.
    builder = SparkSession.builder \
        .appName(cfg["app_name"]) \
        .config("spark.jars.packages", cfg["jars"]["packages"]) \
        .config("spark.sql.extensions", cfg["sql"]["extensions"]) \
        .config("spark.ui.enabled", cfg["ui_enabled"])

    # 3. Dynamic mapping all sub properties from 'local' catalog defined in YAML file.
    # This injects dynamically class, type, warehouse, s3_endpoint, s3_endpoint, s3_access_key_id, etc.
    catalog_props = cfg["catalog"]["local"]
    for key, val in catalog_props.items():
        # Replace underlines from YAML file to dots so the spark syntax (ej: s3_endpoint -> s3.endpoint)
        spark_key = f"spark.sql.catalog.local.{key.replace('_', '.')}"
        builder = builder.config(spark_key, str(val))

    # 4. Inject file system credentials hadoop's global.(fs.s3a) 
    # This is MANDATORY so that Spark's native commands as spark.read.csv("s3a://...") works on Bronze
    builder = builder \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadminpassword") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")

    # 5. Create Active Session.
    spark_session = builder.getOrCreate()
    
    # 6. Post-configurations of  console cleansing.
    spark_session.sparkContext.setLogLevel("ERROR")
    spark_session.sql("USE local")
    
    #clear_output()
    print("¡Spark's session is connected succesfully to Apache Iceberg and MinIO (S3 Local)!")
    
    return spark_session
