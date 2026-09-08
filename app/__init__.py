import os
from datetime import datetime
from flask import Flask, session
from .config import Config
from .models import db


TRANSLATIONS = {
    "fr": {
        "dashboard": "Tableau de bord", "upload_nav": "Importer un document", "faq": "FAQ",
        "contact": "Contact", "about": "À propos", "admin": "Admin", "logout": "Déconnexion",
        "login": "Connexion", "signup": "Inscription", "language": "Langue : français",
        "assistant": "Assistant NovaDoc", "assistant_help": "Pose une question sur les documents ou anomalies.",
        "assistant_send": "Envoyer", "upload_title": "Importer un document.",
        "upload_intro": "Déposez un fichier, choisissez son contexte et laissez NovaDoc extraire les informations essentielles.",
        "new_processing": "Nouveau traitement", "document_type": "Type de document", "ocr_language": "Langue OCR",
        "file_label": "Fichier (PDF, PNG ou JPG)", "choose_file": "Choisir un fichier", "file_hint": "PDF, PNG ou JPG · 16 Mo maximum",
        "start_ocr": "Importer et lancer l'OCR", "how_it_works": "Comment ça marche",
        "simple_flow": "Un flux simple, des données prêtes à l'emploi.", "import_step": "Importez",
        "select_document": "Sélectionnez votre document.", "analyse_step": "Analysez",
        "ocr_identifies": "L'OCR identifie les champs importants.", "use_step": "Exploitez",
        "use_data": "Consultez, filtrez et exportez vos données.", "help_center": "Centre d'aide",
        "faq_title": "Les réponses, sans détour.", "faq_intro": "Tout ce qu'il faut savoir pour importer et exploiter vos documents avec NovaDoc.",
        "contact_kicker": "Parlons de vos flux", "contact_title": "Une question ? Écrivons-nous.",
        "contact_intro": "Notre équipe vous répond au sujet de vos documents, de l'OCR ou de votre espace NovaDoc.",
        "team_available": "Équipe disponible", "contact_detail": "Décrivez votre besoin avec quelques détails. Cela nous permettra de vous répondre plus précisément.",
        "average_delay": "Délai moyen", "one_day": "1 jour ouvré", "send_message": "Envoyer le message",
        "about_kicker": "À propos de NovaDoc", "about_title": "Les documents complexes, enfin lisibles.",
        "about_intro": "NovaDoc OCR transforme les factures, rapports et fiches techniques en informations structurées, prêtes à être contrôlées et utilisées.",
        "collect": "Collecter", "understand": "Comprendre", "decide": "Décider",
        "collect_text": "Importez vos PDF et images depuis un espace unique, pensé pour aller vite.",
        "understand_text": "Notre OCR extrait les numéros, fournisseurs, dates et montants importants.",
        "decide_text": "Filtrez les traitements, repérez les anomalies et exportez vos résultats.",
        "document_intelligence": "Intelligence documentaire", "hero_title": "Transformez vos documents en décisions.",
        "hero_description": "Centralisez, analysez et exploitez automatiquement vos factures, rapports et fiches techniques grâce à un flux OCR fiable.",
        "document_flow": "Flux documentaire", "flow_title": "Une chaîne documentaire claire, du fichier à la décision.", "active": "ACTIF", "reception": "Réception", "automatic": "Automatique",
        "ocr_analysis": "Analyse OCR", "real_time": "En temps réel", "capture": "Capture intelligente",
        "capture_text": "PDF, images et documents techniques", "structured": "Extraction structurée",
        "structured_text": "Les champs clés, sans saisie manuelle", "tracking": "Suivi opérationnel",
        "tracking_text": "Statuts, anomalies et export CSV", "operations_heading": "Une lecture claire de vos opérations",
        "useful_data": "La donnée utile, au bon moment.", "operations_text": "NovaDoc transforme les informations dispersées dans vos documents en une base exploitable. Suivez les volumes, contrôlez les traitements et retrouvez chaque facture depuis un seul espace.",
        "in_motion": "Traitement en mouvement", "document_place": "Chaque document trouve sa place.",
        "processing_text": "Visualisez le parcours d'une facture, de l'importation à l'extraction des données clés.",
        "start_processing": "Lancer un traitement", "processing_active": "Flux OCR actif", "documents_processed": "documents traités",
        "total_documents": "Documents totaux", "successfully_processed": "Traités avec succès", "pending_failure": "En attente / échec",
        "search": "Recherche", "search_placeholder": "Nom, facture, fournisseur...", "type": "Type", "all": "Tous", "quick_filters": "Filtres rapides", "anomalies": "Anomalies",
        "invoice": "Facture", "report": "Rapport", "technical": "Technique", "ocr_status": "Statut OCR",
        "ok": "OK", "failure": "Échec", "pending": "En attente", "start_date": "Date début", "end_date": "Date fin",
        "filter": "Filtrer", "imported_documents": "Documents importés", "documents_description": "Visualisez les factures et documents traités avec le statut de l'OCR.",
        "delete_selected": "Supprimer la sélection", "export_csv": "Exporter CSV", "import_short": "+ Importer", "file": "Fichier",
        "invoice_number": "N° Facture", "supplier": "Fournisseur", "invoice_date": "Date facture", "amount": "Montant TTC",
        "imported_at": "Importé le", "view": "Voir", "no_documents": "Aucun document importé pour l'instant.",
        "supported_documents": "Documents pris en charge", "ready_to_accelerate": "Prêt à accélérer votre gestion ?",
        "import_next": "Importez votre prochain document.", "start_now": "Commencer maintenant", "footer_tagline": "La donnée documentaire, enfin exploitable.",
        "system_operational": "Système opérationnel", "assistant_greeting": "Bonjour ! Demandez-moi de retrouver une facture, d'expliquer une anomalie ou de consulter un fournisseur.",
        "assistant_placeholder": "Exemple : trouve la facture 2024-00123", "assistant_fallback": "Je n'ai pas de réponse pour le moment.",
        "assistant_error": "Erreur de communication avec l'assistant.", "processing": "Analyse...", "ocr_analysis_error": "Erreur d'analyse", "ocr_no_text": "Aucun texte extrait", "close": "Fermer", "select_all": "Sélectionner tout", "delete_confirm": "Supprimer les documents sélectionnés ?",
        "dashboard_title": "Tableau de bord", "upload_page_title": "Importer un document", "faq_page_title": "FAQ - NovaDoc", "contact_page_title": "Contact - NovaDoc", "about_page_title": "À propos - NovaDoc", "select_document": "Sélectionner", "dark_mode": "Activer le mode sombre", "light_mode": "Activer le mode clair",
        "login_kicker": "Espace sécurisé", "login_heading": "Retrouvez le contrôle de vos documents.", "login_side_title": "Votre espace documentaire, en un seul endroit.", "login_side_text": "Consultez vos traitements OCR, suivez les statuts et retrouvez vos factures en quelques secondes.", "login_benefit_one": "Données centralisées", "login_benefit_two": "Traitement OCR suivi", "login_benefit_three": "Accès sécurisé",
        "login_title": "Connexion", "login_intro": "Accédez à votre espace personnel.", "username": "Nom d'utilisateur", "password": "Mot de passe", "login_action": "Se connecter",
        "signup_title": "Créer un compte", "signup_intro": "Inscrivez-vous pour accéder à l'espace utilisateur du site.", "email": "Email", "confirm_password": "Confirmer le mot de passe", "signup_action": "Créer mon compte",
    },
    "en": {
        "dashboard": "Dashboard", "upload_nav": "Upload document", "faq": "FAQ",
        "contact": "Contact", "about": "About", "admin": "Admin", "logout": "Log out",
        "login": "Log in", "signup": "Sign up", "language": "Language: English",
        "assistant": "NovaDoc Assistant", "assistant_help": "Ask a question about documents or anomalies.",
        "assistant_send": "Send", "upload_title": "Upload a document.",
        "upload_intro": "Drop a file, choose its context and let NovaDoc extract the essential information.",
        "new_processing": "New processing", "document_type": "Document type", "ocr_language": "OCR language",
        "file_label": "File (PDF, PNG or JPG)", "choose_file": "Choose a file", "file_hint": "PDF, PNG or JPG · 16 MB maximum",
        "start_ocr": "Upload and start OCR", "how_it_works": "How it works",
        "simple_flow": "A simple flow for ready-to-use data.", "import_step": "Import",
        "select_document": "Select your document.", "analyse_step": "Analyse",
        "ocr_identifies": "OCR identifies the important fields.", "use_step": "Use",
        "use_data": "Review, filter and export your data.", "help_center": "Help center",
        "faq_title": "Answers, without the detour.", "faq_intro": "Everything you need to import and work with documents in NovaDoc.",
        "contact_kicker": "Let's talk about your workflows", "contact_title": "Have a question? Get in touch.",
        "contact_intro": "Our team can help with your documents, OCR or NovaDoc workspace.",
        "team_available": "Team available", "contact_detail": "Describe your needs with a few details so we can give you a precise answer.",
        "average_delay": "Average response", "one_day": "1 business day", "send_message": "Send message",
        "about_kicker": "About NovaDoc", "about_title": "Complex documents, finally readable.",
        "about_intro": "NovaDoc OCR turns invoices, reports and technical sheets into structured information ready to review and use.",
        "collect": "Collect", "understand": "Understand", "decide": "Decide",
        "collect_text": "Upload PDFs and images from one workspace designed for speed.",
        "understand_text": "Our OCR extracts key numbers, suppliers, dates and amounts.",
        "decide_text": "Filter processing results, spot anomalies and export your data.",
        "document_intelligence": "Document intelligence", "hero_title": "Turn documents into decisions.",
        "hero_description": "Centralize, analyse and use invoices, reports and technical sheets automatically through a reliable OCR workflow.",
        "document_flow": "Document flow", "flow_title": "A clear document chain, from file to decision.", "active": "ACTIVE", "reception": "Reception", "automatic": "Automatic",
        "ocr_analysis": "OCR analysis", "real_time": "Real time", "capture": "Smart capture",
        "capture_text": "PDFs, images and technical documents", "structured": "Structured extraction",
        "structured_text": "Key fields, without manual entry", "tracking": "Operational tracking",
        "tracking_text": "Statuses, anomalies and CSV export", "operations_heading": "A clear view of your operations",
        "useful_data": "Useful data, right on time.", "operations_text": "NovaDoc turns scattered document information into an actionable base. Track volumes, monitor processing and find every invoice from one workspace.",
        "in_motion": "Processing in motion", "document_place": "Every document finds its place.",
        "processing_text": "See an invoice move from import to key data extraction.",
        "start_processing": "Start a process", "processing_active": "OCR flow active", "documents_processed": "documents processed",
        "total_documents": "Total documents", "successfully_processed": "Successfully processed", "pending_failure": "Pending / failed",
        "search": "Search", "search_placeholder": "Name, invoice, supplier...", "type": "Type", "all": "All", "quick_filters": "Quick filters", "anomalies": "Anomalies",
        "invoice": "Invoice", "report": "Report", "technical": "Technical", "ocr_status": "OCR status",
        "ok": "OK", "failure": "Failed", "pending": "Pending", "start_date": "Start date", "end_date": "End date",
        "filter": "Filter", "imported_documents": "Imported documents", "documents_description": "View invoices and processed documents with their OCR status.",
        "delete_selected": "Delete selected", "export_csv": "Export CSV", "import_short": "+ Upload", "file": "File",
        "invoice_number": "Invoice no.", "supplier": "Supplier", "invoice_date": "Invoice date", "amount": "Total incl. tax",
        "imported_at": "Imported at", "view": "View", "no_documents": "No documents imported yet.",
        "supported_documents": "Supported documents", "ready_to_accelerate": "Ready to accelerate your workflow?",
        "import_next": "Upload your next document.", "start_now": "Get started", "footer_tagline": "Document data, finally actionable.",
        "system_operational": "System operational", "assistant_greeting": "Hello! Ask me to find an invoice, explain an anomaly or check a supplier.",
        "assistant_placeholder": "Example: find invoice 2024-00123", "assistant_fallback": "I do not have an answer right now.",
        "assistant_error": "Assistant communication error.", "processing": "Analysing...", "ocr_analysis_error": "Analysis error", "ocr_no_text": "No text extracted", "close": "Close", "select_all": "Select all", "delete_confirm": "Delete selected documents?",
        "dashboard_title": "Dashboard", "upload_page_title": "Upload document", "faq_page_title": "FAQ - NovaDoc", "contact_page_title": "Contact - NovaDoc", "about_page_title": "About - NovaDoc", "select_document": "Select", "dark_mode": "Enable dark mode", "light_mode": "Enable light mode",
        "login_kicker": "Secure workspace", "login_heading": "Take control of your documents.", "login_side_title": "Your document workspace, in one place.", "login_side_text": "Review OCR processing, track statuses and find invoices in seconds.", "login_benefit_one": "Centralized data", "login_benefit_two": "Tracked OCR processing", "login_benefit_three": "Secure access",
        "login_title": "Log in", "login_intro": "Access your personal workspace.", "username": "Username", "password": "Password", "login_action": "Log in",
        "signup_title": "Create an account", "signup_intro": "Sign up to access your workspace.", "email": "Email", "confirm_password": "Confirm password", "signup_action": "Create my account",
    },
}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Créer le dossier d'upload s'il n'existe pas
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    @app.context_processor
    def inject_openai_status():
        current_language = session.get("language", "fr")

        def translate(key):
            return TRANSLATIONS.get(current_language, TRANSLATIONS["fr"]).get(key, key)

        return {
            "openai_enabled": bool(app.config.get("OPENAI_API_KEY")),
            "current_year": datetime.now().year,
            "current_language": current_language,
            "tr": translate,
        }

    def _migrate_database():
        from sqlalchemy import inspect, text
        from sqlalchemy.exc import OperationalError

        def _try_add_column(conn, ddl):
            try:
                conn.execute(text(ddl))
            except OperationalError as error:
                message = str(error).lower()
                if "duplicate column name" in message or "duplicate column" in message:
                    return
                raise

        inspector = inspect(db.engine)
        if "document" in inspector.get_table_names():
            existing_columns = [col["name"] for col in inspector.get_columns("document")]
            with db.engine.begin() as conn:
                if "anomalie" not in existing_columns:
                    _try_add_column(conn, "ALTER TABLE document ADD COLUMN anomalie INTEGER DEFAULT 0")
                if "anomalie_raison" not in existing_columns:
                    _try_add_column(conn, "ALTER TABLE document ADD COLUMN anomalie_raison TEXT")
                if "langue" not in existing_columns:
                    _try_add_column(conn, "ALTER TABLE document ADD COLUMN langue TEXT DEFAULT 'fra+eng+ara'")
                if "fournisseur_logo" not in existing_columns:
                    _try_add_column(conn, "ALTER TABLE document ADD COLUMN fournisseur_logo TEXT")
                if "type_panne" not in existing_columns:
                    _try_add_column(conn, "ALTER TABLE document ADD COLUMN type_panne TEXT")
                if "duree_maintenance" not in existing_columns:
                    _try_add_column(conn, "ALTER TABLE document ADD COLUMN duree_maintenance TEXT")

    with app.app_context():
        from . import routes  # noqa: F401  (enregistre les routes)
        db.create_all()  # crée les tables si elles n'existent pas encore
        _migrate_database()

        app.register_blueprint(routes.main_bp)

    return app
