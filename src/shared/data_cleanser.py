from pyspark.sql import DataFrame
import pyspark.sql.functions as F


class DataCleanser:

    def __init__(self):
        """Class for pure transformation, session spark no required, operates over DataFrame."""
        pass

    def remove_duplicates(self, df: DataFrame, subset_columns: list = None) -> DataFrame:
        """
        Eliminates duplicate rows. 
        If 'subset_columns' is passed, then eliminate duplicates based on those columns (ej: Primary Keys).
        """
        if subset_columns:
            print(f"🧹 [Cleanser] Eliminating duplicated based on PK: {subset_columns}")
            return df.dropDuplicates(subset_columns)
        
        print("🧹 [Cleanser] Eliminating exact duplicated based on DataFrame")
        df_deduplicated =  df.dropDuplicates()
        return df_deduplicated

    def impute_nulls(self, df: DataFrame, strategy: dict) -> DataFrame:
        """
         Imputes null values dynamically using the provided strategy in the dict.
         Strategy example: {'voltage': 'mean', 'temperature': 'median', 'status': 'Unknown'}
         """
        print("🧹 [Cleanser] Applying null imputation strategy...")
    
        # Splitting fixed values from statistical computations (mean/median)
        fill_constants = {}
        df_imputed = df

        for column, method in strategy.items():
            if method in ["mean", "median"]:
                # We calculate the statistic value using the aggregation function from Spark.
                agg_func = F.mean(column) if method == "mean" else F.percentile_approx(column, 0.5)
            
                 # SAFE CHECK: Get the Row object first
                row_result = df.select(agg_func).first()
            
             # Only extract the position [0] if the row is not None and has data
            if row_result and row_result[0] is not None:
                fill_constants[column] = row_result[0]
            else:
               # If it is a fixed value (ej: "Unknown" or 0) then it is directly added.
               fill_constants[column] = method

        # We apply the efficient massive imputation using fill() from PySpark
        if fill_constants:
           # Due to Spark limitations, fill() requires the value type to match the column type
           df_imputed = df_imputed.na.fill(fill_constants)
        
        return df_imputed




    def standardize_column_names(self, df: DataFrame) -> DataFrame:
        """Standardizes the columns names to lowercase and replace spaces to underlines efficiently."""
        print("🧹 [Cleanser] Standardizing column names in a single Spark step...")
    
        # 1. We create the transformation list in pure python
        clean_columns = [
            F.col(col).alias(col.strip().lower().replace(" ", "_").replace("-", "_"))
            for col in df.columns
        ]
    
        # 2. We pass the whole list to an unique .select() dunpacked with *
        # This generates A NEW UNIQUE DataFrame in spark faster
        return df.select(*clean_columns)

