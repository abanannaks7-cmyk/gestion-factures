from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """Compte utilisateur du site pour l'accès à l'application."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(200), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Document(db.Model):
    """Représente un document technique ou une facture importée dans le système."""

    id = db.Column(db.Integer, primary_key=True)

    # Infos sur le fichier original
    nom_fichier = db.Column(db.String(255), nullable=False)
    chemin_fichier = db.Column(db.String(500), nullable=False)
    type_document = db.Column(db.String(50), default="facture")  # facture, doc_technique...
    date_upload = db.Column(db.DateTime, default=datetime.utcnow)

    # Résultat brut de l'OCR (tout le texte extrait, utile pour recherche/debug)
    texte_ocr = db.Column(db.Text, nullable=True)
    statut_ocr = db.Column(db.String(20), default="en_attente")  # en_attente, ok, echec

    # Champs extraits automatiquement (peuvent être corrigés manuellement ensuite)
    numero_facture = db.Column(db.String(100), nullable=True)
    fournisseur = db.Column(db.String(255), nullable=True)
    fournisseur_logo = db.Column(db.String(100), nullable=True)
    date_facture = db.Column(db.String(50), nullable=True)
    montant_ttc = db.Column(db.String(50), nullable=True)
    type_panne = db.Column(db.String(255), nullable=True)
    duree_maintenance = db.Column(db.String(100), nullable=True)
    anomalie = db.Column(db.Boolean, default=False)
    anomalie_raison = db.Column(db.String(255), nullable=True)
    langue = db.Column(db.String(50), nullable=True, default="fra+eng+ara")

    def to_dict(self):
        return {
            "id": self.id,
            "nom_fichier": self.nom_fichier,
            "type_document": self.type_document,
            "date_upload": self.date_upload.strftime("%d/%m/%Y %H:%M"),
            "statut_ocr": self.statut_ocr,
            "numero_facture": self.numero_facture,
            "fournisseur": self.fournisseur,
            "fournisseur_logo": self.fournisseur_logo,
            "date_facture": self.date_facture,
            "montant_ttc": self.montant_ttc,
            "type_panne": self.type_panne,
            "duree_maintenance": self.duree_maintenance,
            "anomalie": self.anomalie,
            "anomalie_raison": self.anomalie_raison,
            "langue": self.langue,
        }

    @property
    def logo_asset(self):
        known_logos = {
            "edf", "engie", "total", "sncf", "airbus",
            "orange", "amazon", "apple", "societe_abc",
            "stateco", "nsie",
        }
        if self.fournisseur_logo and self.fournisseur_logo in known_logos:
            return self.fournisseur_logo
        return "fournisseur"


class ContactMessage(db.Model):
    """Stocke les messages envoyés depuis la page de contact."""

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    sujet = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "nom": self.nom,
            "email": self.email,
            "sujet": self.sujet,
            "message": self.message,
            "date_created": self.date_created.strftime("%d/%m/%Y %H:%M"),
        }


class ComplianceAlert(db.Model):
    """Représente une alerte de conformité détectée sur un document."""

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    rule_key = db.Column(db.String(200), nullable=False)
    level = db.Column(db.String(20), nullable=False, default='warning')
    message = db.Column(db.String(1000), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    resolved = db.Column(db.Boolean, default=False)
    resolved_at = db.Column(db.DateTime, nullable=True)

    document = db.relationship('Document', backref=db.backref('compliance_alerts', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'rule_key': self.rule_key,
            'level': self.level,
            'message': self.message,
            'date_created': self.date_created.strftime('%d/%m/%Y %H:%M'),
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.strftime('%d/%m/%Y %H:%M') if self.resolved_at else None,
        }
