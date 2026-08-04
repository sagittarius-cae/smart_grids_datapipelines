# data_io.py
from pyspark.sql import DataFrame
from spark import get_spark_session

class DataIO:
    # Nombre de tu catálogo único para la sesión
    ICEBERG_CATALOG = "local_lakehouse"

    def __init__(self):
        """
        Inicializa DataIO recuperando de forma automática la sesión 
        de PySpark desde spark.py sin parámetros.
        """
        self.spark = get_spark_session()

    def _configure_local_iceberg(self, bucket: str, namespace: str):
        """
        Configura el almacén (warehouse) usando s3a://. 
        Hadoop intercepta esto y lo escribe dentro de los buckets de tu laptop.
        """
        dynamic_warehouse = f"s3a://{bucket}/"
        
        # Le decimos a Iceberg en qué carpeta/bucket operar
        self.spark.conf.set(f"spark.sql.catalog.{self.ICEBERG_CATALOG}", "org.apache.iceberg.spark.SparkCatalog")
        self.spark.conf.set(f"spark.sql.catalog.{self.ICEBERG_CATALOG}.type", "hadoop")
        self.spark.conf.set(f"spark.sql.catalog.{self.ICEBERG_CATALOG}.warehouse", dynamic_warehouse)
        
        # Aseguramos la existencia del Dominio de Negocio (Base de datos)
        self.spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {self.ICEBERG_CATALOG}.{namespace}")

    # --- MÉTODOS DE LECTURA ---

    def read_csv(self, bucket: str, namespace: str, file_name: str) -> DataFrame:
        """Lee el CSV inicial usando la ruta s3a local redirigida."""
        path = f"s3a://{bucket}/{namespace}/{file_name}"
        print(f"📥 [MinIO Local] Leyendo archivo CSV desde: {path}")
        return self.spark.read \
            .option("header", "true") \
            .option("inferSchema", "true") \
            .option("delimiter", ",") \
            .csv(path)

    def read_table(self, bucket: str, namespace: str, entity_name: str) -> DataFrame:
        """Lee la tabla de Iceberg consultando los metadatos locales."""
        self._configure_local_iceberg(bucket, namespace)
        table_name = f"{self.ICEBERG_CATALOG}.{namespace}.{entity_name}"
        print(f"📥 [MinIO Local] Leyendo tabla estructurada: {table_name}")
        return self.spark.read.table(table_name)

    # --- MÉTODOS DE ESCRITURA ---

    def write_table(self, df: DataFrame, bucket: str, namespace: str, entity_name: str, mode: str = "overwrite"):
        """
        Escribe los archivos Parquet reales dentro de tu MinIO local de forma transaccional.
        Físicamente creará: s3a://{bucket}/{namespace}/{entity_name}/data/
        """
        self._configure_local_iceberg(bucket, namespace)
        table_name = f"{self.ICEBERG_CATALOG}.{namespace}.{entity_name}"
        execution_mode = mode.lower()
        
        # Usamos la API avanzada writeTo para un manejo óptimo de Iceberg
        writer = df.writeTo(table_name)

        if execution_mode == "overwrite":
            print(f"🔄 [MinIO Local] Sobreescribiendo tabla de forma ACID: {table_name}")
            writer.createOrReplace()

        elif execution_mode == "append":
            print(f"➕ [MinIO Local] Insertando nuevas filas Parquet en: {table_name}")
            writer.append()
            
        else:
            raise ValueError(f"❌ Modo '{mode}' no soportado. Usa 'append' o 'overwrite'.")
