import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    # Clé secrète Flask (change-la en production, mets-la dans un .env)
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-moi-en-production")

    # Base de données SQLite locale (fichier database.db à la racine du projet)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Dossier où sont stockés les fichiers uploadés (scans/photos de factures)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "uploads")
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

    # Taille max d'un fichier uploadé : 16 Mo
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Langues OCR par défaut : français, anglais, arabe
    OCR_LANGUAGES = os.environ.get("OCR_LANGUAGES", "fra+eng+ara")

    # Clé OpenAI facultative pour activer l'assistant IA
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
    OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

    # Chemin vers l'exécutable Tesseract (utile surtout sous Windows)
    # Exemple Windows : r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    TESSERACT_CMD = os.environ.get("TESSERACT_CMD", None)

    # SMTP / Email (optionnel) — configure dans .env pour activer l'envoi
    SMTP_HOST = os.environ.get("SMTP_HOST")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SMTP_USER")
    SMTP_PASS = os.environ.get("SMTP_PASS")
    EMAIL_FROM = os.environ.get("EMAIL_FROM")

    # Admin simple (utilisé pour protéger les pages d'administration)
    ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
    ADMIN_PASS = os.environ.get("ADMIN_PASS", "password")
