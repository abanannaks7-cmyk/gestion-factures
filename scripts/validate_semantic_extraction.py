from app import create_app
from app.models import db, Document
from app.ocr_utils import extraire_champs_facture

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()

    texte = """
Rapport de maintenance
Type de panne : panne électrique
Durée de maintenance : 3 heures
Total TTC : 450,00 MAD
Facture N° 2024-00123
"""

    champs = extraire_champs_facture(texte)
    print('champs:', champs)

    doc = Document(
        nom_fichier='test.pdf',
        chemin_fichier='/tmp/test.pdf',
        type_document='rapport_maintenance',
        texte_ocr=texte,
        numero_facture='2024-00123',
        date_facture='15/02/2026',
        montant_ttc='450,00',
        fournisseur='EDF',
        type_panne=champs.get('type_panne'),
        duree_maintenance=champs.get('duree_maintenance'),
        statut_ocr='ok',
    )
    db.session.add(doc)
    db.session.commit()

    from app.routes import _run_compliance_checks
    _run_compliance_checks(doc)

    print('anomalie:', doc.anomalie, doc.anomalie_raison)
    print('alerts:', [a.to_dict() for a in doc.compliance_alerts])
