# 📊 SmartGrids Datapiple platform

> Breve descripción de una sola frase que resuma lo que hace tu proyecto (ej. "Pipeline ETL para el procesamiento y análisis de datos CSV utilizando PySpark y almacenamiento MinIO local").

---

## 🎯 Objetivo

* **Main goal:** Ingest smart grids and smart meters raw data from many csv files according to the industry to enabler semantic data.
* **Key benefit:** Allows local simulations about data pipelines under the Medallion Architecture. These data will be used for further data analysis and Feature Engineering.

---

## 🛠️ Technology Stack
 List of components, tools, languages:

* **Language:** [Python](python.og)
* **Data processing:** [PySpark](https://spark.apache.org/docs/latest/api/python/index.html)
* **Object storage:** [MinIO]](https://www.min.io/))
* **Containers:** [Docker](https://shields.io](https://docs.docker.com/compose/)

---

## 📸 Architecture Diagrams / Schemas

![Smart Grids Modules](docs/smart_grid_modules.png)
*Description: Organize the smart grids components under business domains*


---

![Entity Relationship](/docs/smart_grid_erd.png)
*Description: Entity relationship diagram among all entities for the smartgrids*

---

![Star Schema](docs/smart_grid_star_schema.png)
*Description: Smart Grids Star schema useful to optimize queries and facilitate data analysis*



### Jupyter Notebooks
![Notebooks console](http://localhost:8888/lab/workspaces/auto-4/tree/notebooks/)
