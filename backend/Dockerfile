# Utilise une image Python légère
FROM python:3.9-slim

# Définit le répertoire de travail
WORKDIR /app

# Copie le fichier des dépendances dans l'image
COPY requirements.txt .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie le code source dans l'image
COPY . .

# Expose le port 8000 pour l'application
EXPOSE 8000

# Commande par défaut pour lancer l'application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
