# Utilisation d'une image Python légère
FROM python:3.10-slim

# On évite les fichiers .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Répertoire de travail dans le conteneur
WORKDIR /app

# Installation des dépendances système (pour compiler certains paquets si besoin)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copie des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie de tout le dossier projet dans le conteneur
COPY . .

# On ajoute le dossier courant au PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Exposition des ports (API, Streamlit)
EXPOSE 8000 8501

# Par défaut, on ne lance rien (sera surchargé par docker-compose)
CMD ["python", "--version"]