FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Ensure artifacts and upload directories exist
RUN mkdir -p /app/app/ml/artifacts /app/reports /app/uploads /app/data

# Run seed script on startup then launch uvicorn
EXPOSE 8000

CMD ["sh", "-c", "python -m app.seed.seed_database && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
