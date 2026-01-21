FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install wait-for-it script for database readiness
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

# Expose port
EXPOSE 8000

# Create startup script
RUN echo '#!/bin/sh\nset -e\necho "Starting migrations..."\nalembic upgrade head\necho "Migrations complete, starting uvicorn..."\nexec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}' > /app/start.sh && chmod +x /app/start.sh

# Run migrations and start server
# Railway provides $PORT environment variable, default to 8000 for local dev
CMD ["/app/start.sh"]
