from pyspark.sql import SparkSession
from IPython.display import clear_output
import yaml

def get_spark_session(config_path: str = "spark_config.yml") -> SparkSession:
    # 1. Leer archivo YAML
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)["spark"]

    # 2. Inicializar el constructor base con parámetros fijos del YAML
    builder = SparkSession.builder \
        .appName(cfg["app_name"]) \
        .config("spark.jars.packages", cfg["jars"]["packages"]) \
        .config("spark.sql.extensions", cfg["sql"]["extensions"]) \
        .config("spark.ui.enabled", cfg["ui_enabled"])

    # 3. Mapear de forma dinámica todas las sub-propiedades del catálogo 'local' definidas en el YAML
    # Esto inyecta dinámicamente class, type, warehouse, s3_endpoint, s3_access_key_id, etc.
    catalog_props = cfg["catalog"]["local"]
    for key, val in catalog_props.items():
        # Reemplaza los guiones bajos del YAML por puntos para la sintaxis de Spark (ej: s3_endpoint -> s3.endpoint)
        spark_key = f"spark.sql.catalog.local.{key.replace('_', '.')}"
        builder = builder.config(spark_key, str(val))

    # 4. Inyectar credenciales del Sistema de Archivos global de Hadoop (fs.s3a) 
    # Esto es OBLIGATORIO para que comandos nativos de Spark como spark.read.csv("s3a://...") funcionen en Bronze
    builder = builder \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadminpassword") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")

    # 5. Crear la sesión activa
    spark_session = builder.getOrCreate()
    
    # 6. Post-configuraciones de limpieza en consola
    spark_session.sparkContext.setLogLevel("ERROR")
    spark_session.sql("USE local")
    
    clear_output()
    print("¡Sesión de PySpark conectada con éxito a Apache Iceberg y MinIO (S3 Local)!")
    
    return spark_session
