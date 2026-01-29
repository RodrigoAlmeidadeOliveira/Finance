# Procfile for Heroku/Fly.io style deployments
web: cd backend && gunicorn --bind 0.0.0.0:$PORT --workers 4 --threads 2 --worker-class gthread --timeout 120 "app:create_app()"
worker: cd backend && celery -A celery_app worker --loglevel=info
beat: cd backend && celery -A celery_app beat --loglevel=info
