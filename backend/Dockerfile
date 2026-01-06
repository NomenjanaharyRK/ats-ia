FROM python:3.11-slim

WORKDIR /app

# Dépendances système (Tesseract + libs OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tesseract-ocr \
    tesseract-ocr-fra \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
  && rm -rf /var/lib/apt/lists/*

# (Optionnel mais conseillé) mettre pip à jour pour éviter certains bugs
RUN pip install --no-cache-dir --upgrade pip

# 1) Installer PyTorch CPU explicitement
RUN pip install --default-timeout=120 --no-cache-dir \
    torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

# 2) Installer le reste des dépendances Python
COPY requirements.txt /app/requirements.txt
RUN pip install --default-timeout=120 --no-cache-dir -r requirements.txt

# 3) Modèle spaCy FR - Installation via pip (déjà dans requirements.txt)
# Le modèle est installé automatiquement via requirements.txt, pas besoin de cette ligne
# Si requirements.txt contient le modèle, cette étape est redondante et peut causer des erreurs

# Code de l'application
COPY . /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
