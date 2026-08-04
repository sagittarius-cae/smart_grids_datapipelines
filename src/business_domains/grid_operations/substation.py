from spark_setup import get_spark_session
from pyspark.sql import DataFrame
from src.shared.io_utils import DataLakeIO
from src.shared.data_cleanser import DataCleanser



NAMESPACE = "smart_grids"
BRONZE_BUCKET = "bronze"
SILVER_BUCKET = "silver"
GOLD_BUCKET = "gold"
FILE_NAME = "06_substation.csv"
DELTA_TABLE = "local.db_raw.substations"

SUBSTATION_STORAGE_STRATEGY = {
    "voltage": "mean",               # Calcula el promedio de voltaje y llena los nulos
    "current_capacity": "median",    # Usa la mediana para evitar ruido por valores atípicos
    "temperature": "mean",           # Llena nulos de temperatura con el promedio
    "operator_status": "unknown",    # Valor fijo (String) para registros sin estado
    "errorCode": 0                   # Valor fijo (Entero) si no se registró código de error
}self

class SubstationEntity:
     def __init__(self) -> None:
              self.spark = get_spark_session()
              self.io_client = DataLakeIO(self.spark)
              self.current_dataframe = None


     def create_data(self) -> None:
         df =  self.io_client.read_csv(BRONZE_BUCKET, NAMESPACE, FILE_NAME)

         ### TO-DO: Data cleasing, validation, imputation, deduplication
         dc = DataCleanser()
         df_deduplicated = dc.remove_duplicates(df)
         df_imputed_nulls = dc.impute_nulls(df_deduplicated, substation_storage_strategy)
         df_standardized = dc.standardize_column_names(df_imputed_nulls)


         self.io_client.write_table(
            df=df_standardized, 
            bucket=SILVER_BUCKET, 
            namespace=SILVER_BUCKET, 
            entity_name=SUBSTATION_STORAGE_STRATEGY, 
            mode="overwrite"
        )
    


     def get_data(entity_name:str) -> DataFrame:
        # For this entity only is required to get data from SILVER, because is a dim
        return self.io_client.read_table(SILVER_BUCKET, NAMESPACE, entity_name)


    



      


