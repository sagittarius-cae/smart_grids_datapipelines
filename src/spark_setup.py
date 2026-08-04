import yaml
from functools import lru_cache
from pyspark.sql import SparkSession

@lru_cache(maxsize=1)
def get_spark_session(config_path: str = "spark_config.yml") -> SparkSession:
    """
    Lee la configuración desde un archivo YAML y construye una sesión de PySpark
    optimizada para Apache Iceberg y conectividad global con MinIO.
    """
    # 1. Leer el archivo YAML
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)["spark"]

    # 2. Inicializar el constructor con parámetros estructurales básicos
    builder = SparkSession.builder \
        .appName(cfg["app_name"]) \
        .config("spark.jars.packages", cfg["jars"]["packages"]) \
        .config("spark.sql.extensions", cfg["sql"]["extensions"]) \
        .config("spark.ui.enabled", cfg["ui_enabled"])

    # 3. Mapear dinámicamente las credenciales globales de Hadoop (fs.s3a) desde el YAML
    # Esto elimina el hardcoding y mapea directamente propiedades con puntos (.)
    hadoop_props = cfg.get("hadoop", {})
    for key, val in hadoop_props.items():
        # Como en el YAML ya usamos puntos (fs.s3a.endpoint), lo inyectamos directamente
        spark_key = f"spark.hadoop.{key}"
        builder = builder.config(spark_key, str(val))

    # 4. Crear la sesión activa de PySpark
    spark_session = builder.getOrCreate()
    
    # 5. Configuraciones de limpieza de consola posteriores a la creación
    spark_session.sparkContext.setLogLevel("ERROR")
    
    # Nota de Arquitectura: Eliminamos el 'USE local' ya que los catálogos e inicializaciones 
    # de Iceberg ahora se manejan bajo demanda de forma dinámica en tu Utility de persistencia.
    
    print("🚀 ¡Sesión de PySpark inicializada correctamente con soporte Hadoop AWS (MinIO)!")
    
    return spark_session
