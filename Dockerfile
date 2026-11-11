# Study Planner – container image (CS50 Week 7: Docker)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=0 \
    DJANGO_DB_PATH=/data/db.sqlite3

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect CSS into staticfiles/ so WhiteNoise can serve it, and create a
# non-root user plus a folder for the SQLite database.
RUN python manage.py collectstatic --noinput \
    && useradd --create-home appuser \
    && mkdir -p /data && chown -R appuser /data /app
USER appuser

EXPOSE 8000
VOLUME ["/data"]

# Apply migrations, then start the app with gunicorn (a production web server).
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
