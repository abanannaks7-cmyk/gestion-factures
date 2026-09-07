from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_PATH = os.path.join(BASE, 'rapport_structuré.docx')

sections = [
    {
        'title': 'Introduction',
        'paragraphs': [
            'Ce rapport présente l’application web de gestion automatisée des documents techniques et factures. Il décrit le projet de manière structurée, en expliquant l’architecture, les fonctionnalités, le traitement OCR, l’interface utilisateur, la configuration et les perspectives d’évolution.',
            'Chaque section contient des explications détaillées ainsi que des zones réservées pour l’insertion de captures d’écran du site web.',
        ],
        'screenshot': 'Page d’accueil ou tableau de bord principal'
    },
    {
        'title': 'Contexte du projet',
        'paragraphs': [
            'Le besoin est de centraliser les factures et documents techniques, puis d’extraire automatiquement les informations importantes grâce à l’OCR.',
            'Le projet vise à réduire le temps de saisie manuelle, améliorer l’organisation documentaire et faciliter le suivi des documents traités.',
            'Il s’adresse à des utilisateurs qui ont besoin de retrouver rapidement des factures et de vérifier des informations clés sans ouvrir chaque document individuellement.',
        ],
        'screenshot': 'Schéma conceptuel ou page de contexte'
    },
    {
        'title': 'Objectifs fonctionnels',
        'paragraphs': [
            'L’application doit permettre l’import de fichiers PDF et images, l’extraction OCR, l’analyse des données extraites et le stockage structuré en base de données.',
            'Elle doit proposer un tableau de bord clair avec des filtres, des actions en masse et une visibilité sur le statut de traitement de chaque document.',
            'L’objectif est aussi d’offrir une interface simple capable de recevoir des corrections manuelles des données extraites.',
        ],
        'screenshot': 'Liste des objectifs ou page de documentation'
    },
    {
        'title': 'Architecture globale',
        'paragraphs': [
            'L’application est construite avec Flask pour le backend, SQLite pour la base de données, et Bootstrap pour l’interface. Le traitement OCR est assuré par Tesseract via pytesseract, et pdf2image permet de convertir des PDF en images exploitables.',
            'Le code est organisé en modules : gestion des routes, modèles de données, utilitaires OCR et templates HTML.',
            'Cette architecture favorise la maintenance et les évolutions futures, tout en conservant une installation simple et légère.',
        ],
        'screenshot': 'Architecture technique simplifiée'
    },
    {
        'title': 'Structure de la base de données',
        'paragraphs': [
            'Le modèle principal est Document. Il stocke le nom du fichier, le chemin, la date d’import, le texte brut OCR et les champs extraits comme le numéro de facture, le fournisseur, la date et le montant TTC.',
            'Des modèles additionnels gèrent les utilisateurs, les messages de contact et les alertes de conformité.',
            'La base SQLite est suffisante pour un prototype ou une utilisation locale ; elle peut évoluer vers PostgreSQL en production.',
        ],
        'screenshot': 'Schéma de la base de données ou tableau des champs'
    },
    {
        'title': 'Traitement OCR et extraction',
        'paragraphs': [
            'Le module ocr_utils.py exécute l’OCR sur les fichiers importés. Il prend en charge les images et les PDF, et nettoie le texte extrait pour rechercher des informations structurées.',
            'Des règles utilisent des expressions régulières pour identifier numéro de facture, date, montant et fournisseur dans le résultat OCR.',
            'Ce mécanisme est modulable : il peut être adapté aux formats spécifiques des factures d’une entreprise ou enrichi avec un moteur plus avancé.',
        ],
        'screenshot': 'Exemple de résultat OCR ou écran d’import'
    },
    {
        'title': 'Import des documents',
        'paragraphs': [
            'La page d’import permet de choisir un fichier et d’envoyer directement le document au serveur.',
            'Le fichier est sauvegardé sur le serveur et le traitement OCR commence immédiatement après l’enregistrement.',
            'Le système valide le format du fichier et informe l’utilisateur si le document n’est pas pris en charge.',
        ],
        'screenshot': 'Formulaire d’import de document'
    },
    {
        'title': 'Tableau de bord',
        'paragraphs': [
            'Le tableau de bord présente une liste des documents importés, triés par date et avec un statut de traitement clair.',
            'Des filtres permettent de rechercher par texte, type de document, statut OCR et période de date.',
            'Des actions en masse, comme l’export CSV ou la suppression groupée, sont proposées pour faciliter la gestion de plusieurs documents.',
        ],
        'screenshot': 'Tableau de bord principal'
    },
    {
        'title': 'Page détail document',
        'paragraphs': [
            'La page de détail affiche les informations extraites d’un document et le texte OCR brut.',
            'L’utilisateur peut corriger manuellement les champs si l’OCR a commis une erreur.',
            'Une prévisualisation du document est intégrée pour consulter le contenu sans quitter la page.',
        ],
        'screenshot': 'Page detail document et correction des champs'
    },
    {
        'title': 'Assistant virtuel',
        'paragraphs': [
            'Un assistant virtuel est intégré dans la page pour aider l’utilisateur à trouver un document ou à comprendre une anomalie.',
            'Si OpenAI est configuré, l’assistant peut fournir des réponses enrichies ; sinon, il fonctionne en mode local.',
            'Le widget est positionné de manière non intrusive et accessible depuis toutes les pages principales.',
        ],
        'screenshot': 'Assistant virtuel ouvert sur le site'
    },
    {
        'title': 'Gestion des erreurs et retours',
        'paragraphs': [
            'Le système utilise les messages flash de Flask pour informer l’utilisateur des actions réussies ou des erreurs.',
            'Un document mal traité est conservé et signale un statut « échec », afin que l’utilisateur puisse réessayer ou corriger les données.',
            'Les avertissements sont clairs et orientés vers la résolution du problème.',
        ],
        'screenshot': 'Notifications et message d’erreur'
    },
    {
        'title': 'Sécurité et authentification',
        'paragraphs': [
            'Le site protège l’accès aux pages sensibles en vérifiant la session utilisateur avant chaque requête.',
            'Les mots de passe sont hachés et les routes publiques sont limitées aux pages de connexion, d’inscription et d’administration.',
            'Cela garantit que seuls les utilisateurs autorisés peuvent accéder aux documents et aux actions critiques.',
        ],
        'screenshot': 'Page de connexion ou d’administration'
    },
    {
        'title': 'Installation et configuration',
        'paragraphs': [
            'Le projet doit être lancé dans un environnement virtuel Python avec les dépendances listées dans requirements.txt.',
            'Tesseract et Poppler sont requis pour l’OCR et la lecture de PDF, et leur chemin peut être configuré via .env.',
            'L’exécution locale se fait avec python run.py, puis il faut ouvrir http://127.0.0.1:5000 dans le navigateur.',
        ],
        'screenshot': 'Exemples de configuration ou terminal d’installation'
    },
    {
        'title': 'Tests et validation',
        'paragraphs': [
            'Le projet inclut des tests automatisés pour vérifier les routes principales et le comportement du traitement.',
            'La commande python -m unittest tests.test_app -v lance ces tests et permet de valider l’intégrité du code.',
            'Des tests supplémentaires peuvent être ajoutés pour couvrir les fonctions OCR et les actions en masse.',
        ],
        'screenshot': 'Capture d’écran des résultats de tests'
    },
    {
        'title': 'Plan d’évolution',
        'paragraphs': [
            'Plusieurs axes d’amélioration sont possibles : gestion des utilisateurs avancée, pagination, notifications en temps réel, intégration PDF.js pour la prévisualisation, et migration vers une base de données plus robuste.',
            'Ces évolutions permettront de transformer le prototype en une solution professionnelle adaptée à un usage entreprise.',
        ],
        'screenshot': 'Illustration des pistes d’évolution'
    },
    {
        'title': 'Annexes et documentation complémentaire',
        'paragraphs': [
            'Les annexes listent les fichiers importants, les conventions d’architecture, et les règles d’extraction utilisées.',
            'Elles fournissent un guide pour les développeurs qui souhaitent reprendre ou faire évoluer le projet.',
        ],
        'screenshot': 'Annexe et documentation technique'
    },
]


def add_title_page(doc):
    title = doc.add_paragraph()
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    run = title.add_run('Rapport détaillé du projet Gestion Factures')
    run.bold = True
    run.font.size = Pt(28)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    subrun = subtitle.add_run('Analyse du projet, architecture, fonctionnalités et zones de capture d’écran')
    subrun.italic = True
    subrun.font.size = Pt(14)

    doc.add_paragraph()
    date_p = doc.add_paragraph('Date : 27 juillet 2026')
    date_p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    author_p = doc.add_paragraph('Auteur : NovaDoc OCR')
    author_p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    doc.add_page_break()


def add_section(doc, title, paragraphs, screenshot):
    heading = doc.add_heading(title, level=1)
    heading.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
    for paragraph in paragraphs:
        p = doc.add_paragraph(paragraph)
        p.paragraph_format.space_after = Pt(8)
        p.runs[0].font.size = Pt(11)
    doc.add_paragraph()
    placeholder = doc.add_paragraph(f'[Zone réservée pour capture d’écran : {screenshot}]')
    placeholder.runs[0].italic = True
    placeholder.runs[0].font.size = Pt(11)
    placeholder_format = placeholder.paragraph_format
    placeholder_format.space_before = Pt(8)
    placeholder_format.space_after = Pt(8)
    doc.add_paragraph()
    doc.add_page_break()


if __name__ == '__main__':
    document = Document()
    add_title_page(document)
    toc = document.add_heading('Table des matières', level=1)
    toc.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
    for idx, section in enumerate(sections, start=1):
        line = document.add_paragraph(f'{idx}. {section["title"]}')
        line.paragraph_format.left_indent = Pt(12)
    document.add_page_break()

    for section in sections:
        add_section(document, section['title'], section['paragraphs'], section['screenshot'])

    document.save(OUTPUT_PATH)
    print('Saved', OUTPUT_PATH)
