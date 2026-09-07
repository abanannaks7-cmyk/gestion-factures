from copy import deepcopy
import argparse
import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SOURCE = os.path.join(BASE, "rapport_stage_complet_structure_modele.docx")
DEFAULT_TEMPLATE = os.path.join(BASE, "ggjuj.docx")
FALLBACK_TEMPLATE = os.path.join(BASE, "RapportTemlate (2).docx")
DEFAULT_OUTPUT = os.path.join(BASE, "rapport_ggjuj_adapte_projet.docx")
SCREENSHOTS = [
    ("app/static/report_login.png", "Figure 1 : Interface de connexion"),
    ("app/static/report_signup.png", "Figure 2 : Création d'un compte"),
    ("app/static/report_dashboard.png", "Figure 3 : Tableau de bord utilisateur"),
    ("app/static/report_upload.png", "Figure 4 : Formulaire d'import d'un document"),
    ("app/static/report_faq.png", "Figure 5 : Page FAQ"),
    ("app/static/report_about.png", "Figure 6 : Page À propos"),
]

SCREENSHOT_EXPLANATIONS = {
    "report_login.png": (
        "Cette page protège l'accès aux documents. L'utilisateur saisit son adresse "
        "électronique et son mot de passe. Après validation, Flask vérifie les "
        "identifiants, ouvre la session et redirige vers le tableau de bord."
    ),
    "report_signup.png": (
        "Cette interface permet de créer un compte. Le formulaire est contrôlé côté "
        "serveur, puis le mot de passe est haché avant son enregistrement dans la base."
    ),
    "report_dashboard.png": (
        "Le tableau de bord regroupe les indicateurs, la recherche, les filtres et la "
        "liste des documents. Il permet de repérer rapidement les traitements réussis, "
        "en attente ou en erreur."
    ),
    "report_upload.png": (
        "L'utilisateur sélectionne un PDF ou une image et choisit la langue OCR. Le "
        "serveur sécurise le nom, enregistre le fichier, lance Tesseract et conserve "
        "les champs extraits dans Document."
    ),
    "report_faq.png": (
        "La FAQ répond aux questions courantes sur l'import, l'OCR, les formats acceptés "
        "et la consultation des résultats. Elle réduit les erreurs de manipulation."
    ),
    "report_about.png": (
        "La page À propos présente NovaDoc, l'objectif du projet et les technologies "
        "utilisées. Elle donne le contexte fonctionnel de l'application."
    ),
}

PROJECT_SECTIONS = [
    ("STRUCTURE DÉTAILLÉE DU RAPPORT", [
        "Ce rapport présente d'abord le contexte et la problématique, puis les objectifs, l'analyse des besoins et la conception. Il décrit ensuite l'environnement technique, l'implémentation du code, les interfaces réalisées, le traitement OCR, les tests et les perspectives.",
        "Le sommaire doit être mis à jour dans Word avec la commande Références > Mettre à jour la table. Les titres de niveau 1 et de niveau 2 servent à générer automatiquement la table des matières.",
    ]),
    ("ARCHITECTURE ET STRUCTURE DU PROJET", [
        "Le dossier app contient le coeur de l'application Flask. Le fichier __init__.py initialise l'application et la base de données. config.py regroupe les paramètres, models.py définit les entités SQLAlchemy, routes.py contient les routes HTTP et ocr_utils.py réalise l'extraction et l'analyse des documents.",
        "Le dossier templates contient les pages Jinja : base.html fournit la structure commune, index.html présente l'accueil, login.html et signup.html gèrent l'authentification, upload.html permet l'import et detail.html affiche le résultat. Le dossier static contient la feuille de style, les logos et les captures utilisées dans ce rapport.",
        "Le fichier run.py est le point d'entrée du serveur. requirements.txt liste les bibliothèques Python. database.db est créée localement par SQLAlchemy et uploads conserve les fichiers importés.",
    ]),
    ("EXPLICATION DU CODE", [
        "La route d'import vérifie la requête, contrôle l'extension, applique secure_filename, sauvegarde le fichier et crée un objet Document. Le traitement OCR lit une image ou convertit chaque page d'un PDF, puis Tesseract produit le texte brut.",
        "Les fonctions d'extraction recherchent les champs métier avec des expressions régulières et des heuristiques : numéro de facture, fournisseur, date, montant TTC, type de document et informations de maintenance. Le statut du document indique si l'analyse est réussie ou si une vérification manuelle est nécessaire.",
        "Les modèles User, Document, ContactMessage et ComplianceAlert séparent les comptes, les fichiers, les demandes de contact et les anomalies. Les templates affichent les données préparées par les routes, tandis que CSS assure la cohérence visuelle et l'adaptation aux écrans mobiles.",
        "La sécurité repose sur le hachage des mots de passe, la vérification de session pour les pages privées et le nettoyage des noms de fichiers. Pour une mise en production, il faudra ajouter une protection CSRF, une gestion fine des rôles et une configuration stricte des secrets.",
    ]),
    ("DIAGRAMMES À INSÉRER", [
        "Diagramme de cas d'utilisation : placer ici les acteurs Utilisateur et Administrateur ainsi que les actions inscription, connexion, import, consultation, recherche, export et gestion des alertes.",
        "Diagramme de classes : placer ici User, Document, ContactMessage et ComplianceAlert, avec leurs attributs et la relation entre Document et ComplianceAlert.",
        "Diagramme de séquence de l'import : placer ici le scénario Navigateur -> Flask -> stockage -> OCR -> extraction -> base de données -> page de détail.",
        "Diagramme d'activités : placer ici les étapes sélection du fichier, validation, sauvegarde, OCR, extraction, contrôle d'anomalie et affichage du résultat.",
        "Modèle conceptuel de données : placer ici les tables et les clés, notamment document_id utilisé par les alertes de conformité.",
    ]),
    ("FONCTIONNEMENT ET VALIDATION", [
        "Le parcours principal commence par l'inscription ou la connexion. L'utilisateur importe ensuite un document, attend le traitement OCR, consulte les champs détectés et peut filtrer ou exporter les résultats depuis le tableau de bord.",
        "Les tests automatisés vérifient l'authentification, la protection des routes privées, l'import d'un document, l'extraction des champs, le mapping des logos et le fonctionnement de l'assistant en mode local. La commande de validation est : python -m unittest tests.test_app -v.",
    ]),
]


def non_empty_paragraphs(document):
    return [paragraph for paragraph in document.paragraphs if paragraph.text.strip()]


def set_black(paragraph):
    for run in paragraph.runs:
        run.font.color.rgb = RGBColor(0, 0, 0)


def replace_paragraph_text(paragraph, text, bold=False):
    paragraph.text = text
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if paragraph.runs:
        run = paragraph.runs[0]
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0, 0, 0)
        run.bold = bold


def clear_table(table):
    for row in table.rows:
        for cell in row.cells:
            cell.text = ""


def add_screenshots(document):
    document.add_page_break()
    heading = document.add_paragraph("ANNEXE : CAPTURES D'ÉCRAN DE L'APPLICATION")
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    heading.runs[0].bold = True
    heading.runs[0].font.name = "Times New Roman"
    heading.runs[0].font.size = Pt(16)
    heading.runs[0].font.color.rgb = RGBColor(0, 0, 0)

    for relative_path, caption in SCREENSHOTS:
        path = os.path.join(BASE, relative_path)
        if not os.path.exists(path):
            continue
        picture = document.add_picture(path, width=Inches(6.1))
        picture.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption_paragraph = document.add_paragraph(caption)
        caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption_paragraph.runs[0].font.name = "Times New Roman"
        caption_paragraph.runs[0].font.size = Pt(10)
        caption_paragraph.runs[0].italic = True
        caption_paragraph.runs[0].font.color.rgb = RGBColor(0, 0, 0)
        explanation = document.add_paragraph(
            SCREENSHOT_EXPLANATIONS.get(os.path.basename(path), "Explication de l'écran présenté.")
        )
        explanation.paragraph_format.space_after = Pt(14)
        document.add_page_break()


def add_project_content(document):
    document.add_page_break()
    heading = document.add_paragraph("CONTENU DÉTAILLÉ DU PROJET")
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    heading.runs[0].bold = True
    heading.runs[0].font.name = "Times New Roman"
    heading.runs[0].font.size = Pt(18)
    for title, paragraphs in PROJECT_SECTIONS:
        section_heading = document.add_paragraph()
        section_heading.paragraph_format.space_before = Pt(14)
        section_heading.paragraph_format.space_after = Pt(8)
        run = section_heading.add_run(title)
        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(15)
        for text in paragraphs:
            document.add_paragraph(text)
        document.add_paragraph()

    section_heading = document.add_paragraph()
    run = section_heading.add_run("Zones réservées aux schémas")
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(15)
    for label in [
        "Zone diagramme de cas d'utilisation",
        "Zone diagramme de classes",
        "Zone diagramme de séquence",
        "Zone diagramme d'activités",
        "Zone modèle conceptuel de données",
    ]:
        paragraph = document.add_paragraph(
            "[INSÉRER ICI : " + label.upper() + "]"
        )
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_before = Pt(24)
        paragraph.paragraph_format.space_after = Pt(24)
        paragraph.runs[0].italic = True
        paragraph.runs[0].font.size = Pt(12)
        document.add_paragraph("Description du schéma et lien avec les fonctionnalités du projet.")
        document.add_page_break()


def build(template_path, output_path):
    if not os.path.exists(template_path):
        raise FileNotFoundError(
            f"Modèle introuvable : {template_path}. "
            "Copiez ggjuj.docx à la racine du projet ou utilisez --template."
        )

    template = Document(template_path)
    source = Document(SOURCE)

    template_paragraphs = non_empty_paragraphs(template)
    source_paragraphs = non_empty_paragraphs(source)

    # Keep the template's paragraph geometry and formatting while replacing its text.
    for index, paragraph in enumerate(template_paragraphs):
        if index < len(source_paragraphs):
            text = source_paragraphs[index].text
            bold = text.startswith("CHAPITRE") or text in {
                "SOMMAIRE", "REMERCIEMENTS", "RÉSUMÉ", "INTRODUCTION GÉNÉRALE",
                "CONCLUSION GÉNÉRALE", "ANNEXE", "LISTE DES TABLEAUX",
                "LISTE DES FIGURES", "LISTE DES ABRÉVIATIONS",
                "BIBLIOGRAPHIE ET WEBOGRAPHIE",
            }
            replace_paragraph_text(paragraph, text, bold=bold)
        else:
            replace_paragraph_text(paragraph, "")

    # Remove old aviation-specific table content; tables remain available for project data.
    for table in template.tables:
        clear_table(table)

    # Ensure all visible text remains black, as requested.
    for paragraph in template.paragraphs:
        set_black(paragraph)
    for table in template.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    set_black(paragraph)

    add_screenshots(template)
    add_project_content(template)
    template.save(output_path)
    print(f"Rapport clone généré : {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Adapte le contenu du rapport au modèle Word fourni."
    )
    parser.add_argument(
        "--template",
        default=DEFAULT_TEMPLATE if os.path.exists(DEFAULT_TEMPLATE) else FALLBACK_TEMPLATE,
        help="Chemin du modèle Word à utiliser (par défaut : ggjuj.docx).",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Chemin du document Word généré.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    build(arguments.template, arguments.output)
