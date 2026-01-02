# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-deploy.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Set environment variables
ENV HOST=0.0.0.0
ENV PORT=7860
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]
