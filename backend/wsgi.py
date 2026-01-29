"""
WSGI entry point for production deployment.
Used by Gunicorn and other WSGI servers.
"""
from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run()
