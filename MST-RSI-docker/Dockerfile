# Étape 1 : Utiliser une image Python légère
FROM python:3.11-slim

# Configurer l'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Exposer le port Flask
EXPOSE 5000

# Commande pour démarrer Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
