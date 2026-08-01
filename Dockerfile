# 1. Start with a bare-bones Linux + Python image
FROM python:3.11-slim

# 2. Install system dependencies & Java (Required for Apache Spark and Iceberg)
RUN apt-get update && apt-get install -y \
    openjdk-21-jre-headless \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 3. Tell PySpark exactly where to find the Java engine on this Linux system
ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# 4. Global Java 21 options to keep PySpark happy
ENV JDK_JAVA_OPTIONS="--add-opens=java.base/java.lang=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base/java.lang.reflect=ALL-UNNAMED --add-opens=java.base/java.io=ALL-UNNAMED --add-opens=java.base/java.net=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED --add-opens=java.base/java.util.concurrent=ALL-UNNAMED --add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.cs=ALL-UNNAMED --add-opens=java.base/sun.security.action=ALL-UNNAMED"

# 5. Create and set the workspace directory inside the container
WORKDIR /app

# 6. Copy your requirements list and install all data engineering libraries
# 6. Upgrade pip first, then copy requirements list and install libraries
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
    

# 6 Copy the entire src folder into the container's /app/src directory
COPY src/ ./src/

# 7. Open ports for JupyterLab (8888) and the Spark Monitoring UI (4040)
EXPOSE 8888 4040

# 8. Start JupyterLab, allowing connections from your local browser without a password
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
