import os
import unittest
import tempfile
from io import BytesIO
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app import create_app
from app.models import db, Document, User
from app.ocr_utils import extraire_champs_facture
from openai import OpenAIError


class GestionFacturesTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            TESTING=True,
            WTF_CSRF_ENABLED=False,
            SMTP_HOST=None,
            SMTP_USER=None,
            SMTP_PASS=None,
            EMAIL_FROM=None,
        )
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def test_extraction_ocr_parse_facture(self):
        texte = """
        SOCIETE ABC
        Facture N° 2024-00123
        Date : 15/02/2024
        Total TTC : 1 250,00 MAD
        """

        champs = extraire_champs_facture(texte)

        self.assertEqual(champs["numero_facture"], "2024-00123")
        self.assertEqual(champs["date_facture"], "15/02/2024")
        self.assertEqual(champs["montant_ttc"], "1 250,00")
        self.assertEqual(champs["fournisseur"], "SOCIETE ABC")

    def test_unauthenticated_user_is_redirected_to_login(self):
        response = self.client.get("/upload", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_upload_page_and_document_creation(self):
        self.client.post(
            "/signup",
            data={
                "username": "alice",
                "email": "alice@example.com",
                "password": "secret123",
                "confirm_password": "secret123",
            },
            follow_redirects=True,
        )

        response = self.client.get("/upload")
        self.assertEqual(response.status_code, 200)

        data = {
            "type_document": "facture",
            "fichier": (BytesIO(b"fake pdf content"), "facture.pdf"),
        }

        response = self.client.post(
            "/upload",
            data=data,
            content_type="multipart/form-data",
        )

        self.assertEqual(response.status_code, 302)

        with self.app.app_context():
            doc = Document.query.first()
            self.assertIsNotNone(doc)
            self.assertEqual(doc.type_document, "facture")

    def test_logo_asset_mapping(self):
        with self.app.app_context():
            doc = Document(
                nom_fichier="facture.pdf",
                chemin_fichier="/tmp/facture.pdf",
                type_document="facture",
                fournisseur="ENGIE Maroc",
                fournisseur_logo="engie",
            )
            self.assertEqual(doc.logo_asset, "engie")

            doc.fournisseur_logo = "unknown_supplier"
            self.assertEqual(doc.logo_asset, "fournisseur")

    def test_signup_and_login_work(self):
        response = self.client.post(
            "/signup",
            data={
                "username": "alice",
                "email": "alice@example.com",
                "password": "secret123",
                "confirm_password": "secret123",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            user = User.query.filter_by(username="alice").first()
            self.assertIsNotNone(user)

        response = self.client.post(
            "/login",
            data={"username": "alice", "password": "secret123"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Tableau de bord", response.data)

    def test_logout_clears_admin_and_user_sessions(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'alice'
            sess['admin_authenticated'] = True

        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as sess:
            self.assertNotIn('user_id', sess)
            self.assertNotIn('username', sess)
            self.assertNotIn('admin_authenticated', sess)

    def test_assistant_query_returns_response(self):
        response = self.client.post(
            "/assistant/query",
            json={"message": "Trouve une facture"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("document", data["answer"].lower())

    def test_assistant_falls_back_without_exposing_openai_error(self):
        self.app.config["OPENAI_API_KEY"] = "dummy"

        with patch("app.routes.OpenAI") as openai_cls:
            openai_cls.return_value.chat.completions.create.side_effect = OpenAIError("quota exceeded")
            response = self.client.post(
                "/assistant/query",
                json={"message": "bonjour"},
            )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsNone(data.get("error"))
        self.assertTrue(any(token in data["answer"].lower() for token in ["je peux", "trouve la facture", "anomalie"]))

    def test_language_switch_renders_english_pages(self):
        response = self.client.get("/set-language/en?next=/faq")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/faq")

        with self.client.session_transaction() as sess:
            sess["user_id"] = 1

        response = self.client.get("/faq")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Answers, without the detour.", response.data)
        self.assertIn(b"Language: English", response.data)


if __name__ == "__main__":
    unittest.main()
