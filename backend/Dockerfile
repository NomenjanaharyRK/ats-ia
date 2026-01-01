FROM python:3.11-slim

WORKDIR /app

# Dépendances système (inclut Tesseract + langue FR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tesseract-ocr \
    tesseract-ocr-fra \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
  && rm -rf /var/lib/apt/lists/*

# Installation des dépendances Python
COPY requirements.txt /app/requirements.txt
RUN pip install --default-timeout=120 --no-cache-dir -r requirements.txt

# Code de l'application
COPY . /app

# Commande par défaut : serveur FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
