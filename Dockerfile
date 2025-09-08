FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads outputs cache

# Expose port (Railway will set PORT variable)
EXPOSE $PORT

# Health check
HEALTHCHECK CMD curl --fail http://localhost:$PORT/_stcore/health

# Run the application
CMD streamlit run main.py --server.port=$PORT --server.address=0.0.0.0
