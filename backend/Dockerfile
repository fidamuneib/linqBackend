# Use Python slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies for mysqlclient
RUN apt-get update && \
    apt-get install -y gcc g++ \
    libmysqlclient-dev default-libmysqlclient-dev \
    build-essential pkg-config \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy all source files
COPY . .

# Port (optional)
EXPOSE 8000

# Default start command
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
