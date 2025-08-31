# Imagen base
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=qrmenu_backend.settings.production

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Migraciones y comando de inicio
CMD python manage.py migrate && gunicorn qrmenu_backend.wsgi:application --bind 0.0.0.0:$PORT
