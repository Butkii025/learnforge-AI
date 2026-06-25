FROM python:3.10-slim

WORKDIR /app

# Install dependencies first for caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend project files into backend/ inside the container
COPY backend/ ./backend

EXPOSE 8000

# Set python path to find backend modules correctly
ENV PYTHONPATH=/app

# Default command matching railway.toml
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
