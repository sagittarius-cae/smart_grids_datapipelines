# 1. Comenzar con una imagen Linux liviana con Python incorporado
FROM python:3.11-slim

# 2. Instalar dependencias del sistema y Java (Requerido para Apache Spark e Iceberg)
RUN apt-get update && apt-get install -y \
    openjdk-21-jre-headless \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 3. Indicar a PySpark exactamente dónde encontrar el motor Java en este sistema Linux
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# 4. Opciones globales de Java 21 para mantener estable a PySpark y sus accesos internos
ENV JDK_JAVA_OPTIONS="--add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base/java.lang.reflect=ALL-UNNAMED --add-opens=java.base/java.io=ALL-UNNAMED --add-opens=java.base/java.net=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.util.concurrent=ALL-UNNAMED --add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.cs=ALL-UNNAMED --add-opens=java.base/sun.security.action=ALL-UNNAMED"

# 5. Crear y establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 6. Copiar la lista de dependencias actualizadas e instalar todas las herramientas de ingeniería
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. Copiar la carpeta local src dentro del directorio /app/src del contenedor
COPY src/ ./src/

# 8. Exponer puertos de red para JupyterLab (8888) y Spark UI (4040)
EXPOSE 8888 4040

# 9. Iniciar JupyterLab permitiendo conexiones desde el navegador local sin contraseñas
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
