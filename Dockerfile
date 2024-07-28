FROM python:3.11-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y gcc default-libmysqlclient-dev pkg-config && \
    apt-get clean

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Collect static files


CMD ["celery", "-A", "myproject", "worker", "-l", "info"]
