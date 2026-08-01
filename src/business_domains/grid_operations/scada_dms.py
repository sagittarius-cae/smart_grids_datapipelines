from spark_setup import get_spark_session
from pyspark.sql import DataFrame
from src.shared.io_utils import DataLakeIO


class SCADADMSEntity:
     def __init__(self) -> None:
              self.spark = get_spark_session()
              self.io_client = DataLakeIO(self.spark)

     def create_rawdata(self) -> None:
         df =  self.io_client.read_csv("05_scada_dms.csv") 
         self.io_client.write_delta_table(self.spark, df, "local.db_raw.scada_dms") 


     def get_data(self, table_name: str) -> DataFrame:
         return self.io_client.read_parquet(table_name)