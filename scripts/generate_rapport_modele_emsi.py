from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT = os.path.join(BASE, "rapport_stage_complet_structure_modele.docx")

def page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    run._r.append(field)


def setup(document):
    section = document.sections[0]
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.95)
    section.right_margin = Inches(0.85)
    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(8)
    for style_name, size in [("Title", 28), ("Heading 1", 21), ("Heading 2", 15)]:
        style = document.styles[style_name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(0, 0, 0)
    for section in document.sections:
        page_number(section.footer.paragraphs[0])


def centered(document, text, size=14, bold=False, italic=False):
    p = document.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor(0, 0, 0)
    r.bold = bold
    r.italic = italic
    return p


def title_page(document):
    for _ in range(2):
        document.add_paragraph()
    centered(document, "ÉCOLE : [Nom de l'établissement]", 15, True)
    centered(document, "Filière : Ingénierie Informatique et Réseaux", 13)
    document.add_paragraph()
    centered(document, "Rapport de stage", 28, True)
    centered(document, "3ème année - Ingénierie Informatique et Réseaux", 16, True)
    document.add_paragraph()
    centered(document, "Projet : Application web de gestion automatisée des factures", 15, True)
    centered(document, "et des documents techniques", 15, True)
    for _ in range(3):
        document.add_paragraph()
    centered(document, "Réalisé par : [Prénom et Nom]", 13, True)
    centered(document, "Encadré par :", 13, True)
    centered(document, "Tuteur de l'école : [Prénom et Nom]", 12)
    centered(document, "Tuteur de stage : [Prénom et Nom]", 12)
    document.add_paragraph()
    centered(document, "Entreprise : [Nom de l'entreprise]", 12)
    centered(document, "Activité : [Activité de l'entreprise]", 12)
    centered(document, "Adresse : [Adresse]", 12)
    document.add_paragraph()
    centered(document, "Période de stage : du [date] au [date]", 13, True)
    document.add_page_break()


def section_page(document, title, paragraphs=None, subsections=None, placeholder=None, images=None):
    document.add_heading(title, level=1)
    if paragraphs:
        for text in paragraphs:
            document.add_paragraph(text)
    if subsections:
        for heading, texts in subsections:
            document.add_heading(heading, level=2)
            for text in texts:
                document.add_paragraph(text)
    if placeholder:
        p = document.add_paragraph("[Insérer ici : " + placeholder + "]")
        p.runs[0].italic = True
        p.runs[0].font.size = Pt(10)
    if images:
        for image_path, caption in images:
            if os.path.exists(image_path):
                picture = document.add_picture(image_path, width=Inches(6.2))
                picture.alignment = WD_ALIGN_PARAGRAPH.CENTER
                caption_paragraph = document.add_paragraph(caption)
                caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                caption_paragraph.runs[0].italic = True
                caption_paragraph.runs[0].font.size = Pt(10)
    document.add_page_break()


def contents(document):
    document.add_heading("SOMMAIRE", level=1)
    main_items = [
        "REMERCIEMENTS ................................................................................. 1",
        "LISTE DES TABLEAUX ........................................................................... 4",
        "LISTE DES FIGURES ............................................................................... 5",
        "LISTE DES ABRÉVIATIONS ................................................................... 6",
        "RÉSUMÉ .................................................................................................. 7",
        "INTRODUCTION GÉNÉRALE ................................................................. 8",
    ]
    chapters = [
        ("CHAPITRE 1 : CADRE DU PROJET .................................................... 9", [
            "1. Introduction", "2. Présentation de l'entreprise", "3. Conclusion",
        ]),
        ("CHAPITRE 2 : ANALYSE DES BESOINS ........................................... 10", [
            "1. Introduction", "2. Le but de l'application", "3. Définitions des données",
            "4. Les besoins fonctionnels", "5. Les besoins non fonctionnels",
            "6. L'étude de l'existant", "7. Conclusion",
        ]),
        ("CHAPITRE 3 : INTÉRÊT DE LA MODÉLISATION ............................ 11", [
            "1. Introduction", "2. Choix de la méthodologie de conception", "3. Conclusion",
        ]),
        ("CHAPITRE 4 : ANALYSE ET CONCEPTION ...................................... 12", [
            "1. Introduction", "2. Dictionnaire de données", "3. Diagramme de classes",
            "4. Diagramme de cas d'utilisation", "5. Modèle conceptuel de données",
            "6. Diagramme de séquence", "7. Diagramme d'activités", "8. Conclusion",
        ]),
        ("CHAPITRE 5 : ENVIRONNEMENT DE TRAVAIL ............................... 13", [
            "1. Introduction", "2. Environnement matériel", "3. Environnement logiciel",
            "4. Technologies utilisées", "5. Conclusion",
        ]),
        ("CHAPITRE 6 : PRÉSENTATION DE L'APPLICATION ....................... 14", [
            "1. Introduction", "2. Interfaces de l'application", "3. Conclusion",
        ]),
    ]
    final_items = [
        "CONCLUSION GÉNÉRALE .................................................................... 15",
        "BIBLIOGRAPHIE ET WEBOGRAPHIE ................................................ 16",
        "ANNEXE .................................................................................................. 17",
    ]
    for item in main_items + final_items:
        document.add_paragraph(item)
    for chapter, subitems in chapters:
        paragraph = document.add_paragraph(chapter)
        paragraph.runs[0].bold = True
        for subitem in subitems:
            paragraph = document.add_paragraph(subitem)
            paragraph.paragraph_format.left_indent = Inches(0.25)
    document.add_page_break()


def build():
    document = Document()
    setup(document)
    title_page(document)
    contents(document)
    section_page(document, "REMERCIEMENTS", [
        "Je tiens à exprimer ma gratitude à toutes les personnes qui ont contribué au bon déroulement de mon stage et à la réalisation de ce projet.",
        "Je remercie particulièrement mon encadrant pédagogique pour ses conseils, son suivi et ses remarques constructives. J'adresse également mes remerciements à mon tuteur de stage et à l'ensemble de l'équipe de l'entreprise pour son accueil et son accompagnement.",
        "Enfin, je remercie ma famille et mes proches pour leur soutien tout au long de cette expérience.",
    ])
    section_page(document, "LISTE DES TABLEAUX", [
        "Tableau 1 : Principales entités de la base de données",
        "Tableau 2 : Technologies et rôles dans l'application",
        "Tableau 3 : Résultats des tests automatisés",
    ])
    section_page(document, "LISTE DES FIGURES", [
        "Figure 1 : Interface de connexion",
        "Figure 2 : Tableau de bord utilisateur",
        "Figure 3 : Formulaire d'import d'un document",
        "Figure 4 : Page FAQ",
        "Figure 5 : Page À propos",
    ])
    section_page(document, "LISTE DES ABRÉVIATIONS", [
        "OCR : Optical Character Recognition, ou reconnaissance optique de caractères.",
        "PDF : Portable Document Format.",
        "CSV : Comma-Separated Values.",
        "API : Application Programming Interface.",
        "UML : Unified Modeling Language.",
        "SQL : Structured Query Language.",
    ])
    section_page(document, "RÉSUMÉ", [
        "Ce rapport présente la conception et le développement d'une application web destinée à automatiser la gestion des factures et des documents techniques. L'application permet d'importer des fichiers PDF ou des images, d'en extraire le texte avec Tesseract OCR et d'identifier automatiquement des informations telles que le numéro de facture, le fournisseur, la date et le montant TTC.",
        "La solution repose sur Flask, SQLAlchemy et SQLite. Elle propose également une authentification, un tableau de bord avec recherche et filtres, un export CSV, la détection d'anomalies et un assistant virtuel. Les tests automatisés valident les fonctions principales du système.",
        "Mots-clés : Flask, OCR, Tesseract, facture, Python, SQLite, application web.",
    ])
    section_page(document, "INTRODUCTION GÉNÉRALE", [
        "La transformation numérique des entreprises entraîne une augmentation du volume de documents à traiter. Les factures et rapports techniques contiennent des informations importantes, mais leur saisie et leur classement manuels sont longs et peuvent générer des erreurs.",
        "L'objectif de ce stage était de développer une application capable de centraliser ces documents et d'automatiser une partie de leur traitement. Le projet combine une interface web, une base de données et un module de reconnaissance optique de caractères.",
        "Le rapport est organisé en six chapitres. Le premier présente le cadre du projet, le deuxième analyse les besoins, le troisième explique l'intérêt de la modélisation, le quatrième détaille la conception, le cinquième présente l'environnement de travail et le dernier décrit l'application réalisée.",
    ])
    section_page(document, "CHAPITRE 1 : CADRE DU PROJET", subsections=[
        ("1. Introduction", ["Ce chapitre situe le projet dans son contexte professionnel et présente le besoin auquel l'application apporte une réponse.", "La gestion des factures est une activité quotidienne qui exige de conserver les documents, de retrouver rapidement leurs informations et de contrôler les montants enregistrés. Le projet répond à ce besoin par une solution web accessible depuis un navigateur."]),
        ("2. Présentation de l'entreprise", ["L'entreprise d'accueil devra être présentée avec son nom, son secteur d'activité, ses services, son organisation et sa place dans son environnement professionnel. Dans le cadre de ce projet, l'entreprise est considérée comme une structure qui reçoit et traite régulièrement des factures et des documents techniques.", "La solution s'inscrit dans une démarche de dématérialisation. Elle permet de réduire le classement manuel, de centraliser les documents et de faciliter leur consultation par les utilisateurs autorisés.", "L'application peut être adaptée aux procédures internes et aux formats utilisés par les fournisseurs. Les règles d'extraction sont regroupées dans un module indépendant afin de pouvoir être ajustées sans modifier toute l'application."]),
        ("3. Conclusion", ["L'étude du contexte montre l'intérêt d'une solution centralisée capable de réduire les opérations manuelles et d'améliorer l'accès aux informations. Elle justifie le choix d'une application web associée à un traitement OCR."]),
    ], placeholder="logo et présentation de l'entreprise")
    section_page(document, "CHAPITRE 2 : ANALYSE DES BESOINS", subsections=[
        ("1. Introduction", ["L'analyse des besoins permet de transformer le problème métier en fonctionnalités concrètes et vérifiables. Elle distingue les utilisateurs, les données manipulées, les règles de traitement et les contraintes techniques."]),
        ("2. Le but de l'application", ["Le but est de permettre l'import, l'analyse, le classement, la consultation et l'export de factures et de documents techniques depuis une interface web sécurisée.", "Le résultat attendu est une fiche documentaire contenant le fichier original, le texte OCR et les informations extraites. L'utilisateur peut ensuite rechercher une facture par son nom, son numéro, son fournisseur, son montant, son type ou son statut."]),
        ("3. Définitions des données", ["Un document possède un nom, un type, un chemin de stockage, une date d'import, un texte OCR et un statut. Les données extraites comprennent le numéro de facture, le fournisseur, la date, le montant TTC, le type de panne et la durée de maintenance.", "Le modèle User représente les comptes. ContactMessage conserve les demandes envoyées depuis le formulaire de contact. ComplianceAlert enregistre les contrôles et les anomalies associés à un document."]),
        ("4. Les besoins fonctionnels", ["L'utilisateur doit pouvoir s'inscrire, se connecter et se déconnecter. Il doit pouvoir importer un PDF ou une image, choisir la langue OCR, consulter le résultat, filtrer les documents, exporter les données et supprimer un document.", "Le système doit classer automatiquement les documents, calculer des indicateurs, signaler certains montants inhabituels, conserver les erreurs OCR et fournir un assistant pour rechercher des documents ou expliquer une anomalie."]),
        ("5. Les besoins non fonctionnels", ["L'application doit être simple à utiliser, responsive, maintenable et suffisamment sécurisée. Elle doit informer l'utilisateur des erreurs et conserver les documents même lorsque l'OCR échoue.", "Le temps de réponse doit rester acceptable pour un document courant. Les paramètres sensibles doivent être séparés du code dans un fichier .env et les mots de passe doivent être hachés avant leur stockage."]),
        ("6. L'étude de l'existant", ["Le classement manuel des fichiers et la saisie dans des tableurs permettent une organisation de base, mais ils ne fournissent pas une recherche centralisée ni une extraction automatique. La solution proposée améliore ces limites.", "Les outils OCR génériques peuvent lire le texte mais ne proposent pas toujours une organisation adaptée aux factures. L'application combine donc la reconnaissance de texte et un modèle métier spécialisé dans les champs utiles."]),
        ("7. Conclusion", ["Les besoins identifiés justifient la mise en place d'une application web modulaire associant traitement documentaire et stockage structuré. Ils servent de référence pour la conception, le développement et les tests."]),
    ])
    section_page(document, "CHAPITRE 3 : INTÉRÊT DE LA MODÉLISATION", subsections=[
        ("1. Introduction", ["La modélisation permet de représenter le système avant et pendant son développement. Elle facilite la communication, la vérification des besoins et l'organisation du code.", "Dans ce projet, elle permet de relier les pages visibles par l'utilisateur aux routes Flask, aux modèles de données et au traitement OCR."]),
        ("2. Choix de la méthodologie de conception", ["Une démarche itérative a été retenue. Les fonctionnalités ont été développées par étapes : création de l'application Flask, conception des modèles, ajout des routes, intégration de l'OCR, réalisation des interfaces et mise en place des tests.", "Les diagrammes UML sont adaptés pour représenter les acteurs, les cas d'utilisation, les classes et les séquences principales du système. Cette méthode permet de détecter les oublis avant l'implémentation et de documenter les choix réalisés.", "Le développement a suivi un cycle simple : analyse du besoin, conception, codage, test, correction et amélioration. Cette organisation est particulièrement utile pour un projet comportant plusieurs composants techniques."]),
        ("3. Conclusion", ["La modélisation réduit les ambiguïtés et fournit une base claire pour passer de l'analyse à l'implémentation. Elle facilite également la maintenance par un autre développeur."]),
    ], placeholder="diagramme UML général")
    section_page(document, "CHAPITRE 4 : ANALYSE ET CONCEPTION", subsections=[
        ("1. Introduction", ["Ce chapitre décrit les principaux éléments de conception de l'application. Il présente les données, les acteurs et le déroulement des traitements."]),
        ("2. Dictionnaire de données", ["Les entités principales sont User pour les comptes, Document pour les fichiers et données OCR, ContactMessage pour les messages et ComplianceAlert pour les alertes. Le modèle Document constitue l'entité centrale.", "Les champs Document comprennent notamment id, nom_fichier, chemin_fichier, type_document, date_upload, texte_ocr, statut_ocr, numero_facture, fournisseur, date_facture, montant_ttc, langue, anomalie et anomalie_raison.", "Les statuts OCR utilisés sont en_attente, ok et echec. Cette information permet de différencier un document en cours de traitement, un document correctement analysé et un document qui nécessite une vérification."]),
        ("3. Diagramme de classes", ["La classe Document est associée aux alertes de conformité. Les classes User, ContactMessage et ComplianceAlert sont gérées par SQLAlchemy et correspondent aux tables de la base.", "La séparation des classes permet de faire évoluer les comptes, les documents et les alertes indépendamment. Les méthodes to_dict facilitent la préparation des données pour les réponses JSON ou les exports."]),
        ("4. Diagramme de cas d'utilisation", ["L'utilisateur peut s'inscrire, se connecter, importer un document, consulter le tableau de bord, filtrer les résultats, visualiser un document, exporter les données et interroger l'assistant. L'administrateur peut gérer les alertes et les messages.", "Le système vérifie la session avant l'accès aux pages privées. Les routes publiques sont limitées aux écrans d'authentification et aux services explicitement nécessaires."]),
        ("5. Modèle conceptuel de données", ["Le modèle relie les documents aux alertes par l'identifiant document_id. Les champs extraits sont conservés dans la table Document afin de permettre la recherche et l'export.", "La base SQLite est créée automatiquement au démarrage par db.create_all. Une migration interne ajoute certaines colonnes lorsque la base existante provient d'une version précédente du projet."]),
        ("6. Diagramme de séquence", ["Lors d'un import, le navigateur transmet le fichier à Flask. Le serveur le sécurise et l'enregistre, crée le document, appelle Tesseract, analyse le texte, met à jour la base et redirige l'utilisateur vers la page de détail.", "Après le commit principal, les contrôles de conformité sont exécutés avec l'identifiant du document disponible. L'utilisateur reçoit ensuite un message indiquant le succès ou l'échec du traitement."]),
        ("7. Diagramme d'activités", ["Le workflow comprend la sélection du fichier, la vérification de l'extension, la sauvegarde, l'OCR, l'extraction, la détection des anomalies, le contrôle de conformité et l'affichage du résultat.", "Une exception OCR ne supprime pas le fichier : le document est conservé avec le statut echec. Cette décision permet une analyse manuelle ou un nouveau traitement ultérieur."]),
        ("8. Conclusion", ["La conception retenue sépare les responsabilités et permet de faire évoluer indépendamment l'interface, le traitement OCR et la persistance. Elle donne également une base claire pour ajouter une file de traitement asynchrone ou une base PostgreSQL."]),
    ], placeholder="diagrammes de conception UML")
    section_page(document, "CHAPITRE 5 : ENVIRONNEMENT DE TRAVAIL", subsections=[
        ("1. Introduction", ["Le projet a été développé dans un environnement local adapté au développement Python et aux traitements OCR. Les outils ont été choisis pour leur simplicité d'installation et leur compatibilité avec une application web légère."]),
        ("2. Environnement matériel", ["Un ordinateur de développement équipé d'un processeur moderne, d'une mémoire suffisante et d'un espace de stockage pour les fichiers importés est nécessaire. Une connexion Internet peut être utilisée pour l'installation des dépendances et l'assistant distant.", "Le traitement OCR dépend aussi de la qualité des documents. Des images nettes, bien cadrées et suffisamment contrastées donnent de meilleurs résultats."]),
        ("3. Environnement logiciel", ["Le projet utilise Windows ou un système compatible, Python 3, Visual Studio Code, un environnement virtuel et un navigateur web. Tesseract OCR et Poppler sont installés pour traiter les images et les PDF.", "Le fichier requirements.txt installe Flask, Flask-SQLAlchemy, pytesseract, Pillow, pdf2image, python-dotenv et OpenAI. Le serveur est lancé par le fichier run.py sur le port 5000."]),
        ("4. Technologies utilisées", ["Python et Flask assurent le backend. Flask-SQLAlchemy et SQLite gèrent les données. Jinja, HTML, CSS et Bootstrap construisent l'interface. pytesseract, Pillow et pdf2image réalisent l'OCR. unittest permet la validation automatisée.", "Werkzeug est utilisé pour le hachage des mots de passe et la sécurisation des noms de fichiers. python-dotenv charge les paramètres du fichier .env. L'intégration OpenAI est facultative et un mode local est prévu si la clé n'est pas disponible."]),
        ("5. Conclusion", ["L'environnement choisi est léger, accessible et adapté au prototypage d'une application de traitement documentaire. Il peut évoluer vers une architecture de production avec PostgreSQL, stockage objet et serveur WSGI."]),
    ], placeholder="capture de Visual Studio Code et terminal")
    section_page(document, "CHAPITRE 6 : PRÉSENTATION DE L'APPLICATION", subsections=[
        ("1. Introduction", ["Ce chapitre présente le fonctionnement visible de l'application et le parcours principal de l'utilisateur. Les captures d'écran intégrées montrent les interfaces réellement obtenues avec le serveur Flask."]),
        ("2. Interfaces de l'application", ["L'application comporte une page de connexion et d'inscription, un tableau de bord, une page d'import, une page de détail, une FAQ, une page de contact et des interfaces d'administration.", "La page de connexion protège l'accès au tableau de bord. L'inscription crée un compte avec un mot de passe haché. La navigation commune permet d'accéder rapidement aux fonctions principales.", "Le tableau de bord affiche les statistiques et les documents avec des filtres. La recherche porte sur le nom du fichier, le numéro de facture, le fournisseur et le montant. Les statuts permettent d'identifier les documents réussis ou en échec.", "La page d'import accepte les fichiers autorisés et permet de choisir la langue OCR. Après l'envoi, le document est enregistré puis traité. La page de détail affiche le fichier, le texte OCR, les champs extraits, le fournisseur et les éventuelles anomalies.", "L'interface fournit des messages de succès ou d'erreur. L'assistant virtuel permet de rechercher une facture, un fournisseur ou une anomalie. L'export CSV facilite la réutilisation des données dans un tableur."]),
        ("3. Conclusion", ["L'application fournit un parcours complet et cohérent, depuis l'authentification jusqu'à la consultation et à l'export des documents. Les captures confirment le fonctionnement des principales interfaces et rendent la présentation du projet plus concrète."]),
    ], images=[
        (os.path.join(BASE, "app", "static", "report_login.png"), "Figure 1 : Interface de connexion"),
        (os.path.join(BASE, "app", "static", "report_dashboard.png"), "Figure 2 : Tableau de bord utilisateur"),
        (os.path.join(BASE, "app", "static", "report_upload.png"), "Figure 3 : Formulaire d'import d'un document"),
        (os.path.join(BASE, "app", "static", "report_faq.png"), "Figure 4 : Page FAQ"),
        (os.path.join(BASE, "app", "static", "report_about.png"), "Figure 5 : Page À propos"),
    ])
    section_page(document, "CONCLUSION GÉNÉRALE", [
        "Ce stage a permis de concevoir et de développer une application web capable d'automatiser une partie de la gestion des factures et des documents techniques. Le système associe authentification, stockage structuré, OCR, extraction de données, recherche, export et détection d'anomalies.",
        "La réalisation de ce projet a permis de mettre en pratique les connaissances en Python, développement web, bases de données, traitement d'images, sécurité et tests. Elle a également montré l'importance de l'analyse des besoins et de la modélisation.",
        "Des évolutions sont possibles : traitement asynchrone, pagination, migration vers PostgreSQL, stockage objet, extraction plus avancée et gestion détaillée des rôles. Le prototype constitue une base solide pour une utilisation professionnelle.",
    ])
    section_page(document, "BIBLIOGRAPHIE ET WEBOGRAPHIE", [
        "Documentation officielle de Flask : https://flask.palletsprojects.com/",
        "Documentation de Flask-SQLAlchemy : https://flask-sqlalchemy.palletsprojects.com/",
        "Documentation de Tesseract OCR : https://tesseract-ocr.github.io/",
        "Documentation de pytesseract : https://pypi.org/project/pytesseract/",
        "Documentation de pdf2image : https://pypi.org/project/pdf2image/",
        "Documentation Python : https://docs.python.org/3/",
    ])
    section_page(document, "ANNEXE", [
        "Annexe 1 : arborescence du projet.",
        "Annexe 2 : extrait du modèle Document.",
        "Annexe 3 : exemple de document traité par OCR.",
        "Annexe 4 : résultats des tests automatisés.",
        "Annexe 5 : guide d'installation : création de l'environnement virtuel, installation de requirements.txt, configuration de Tesseract et lancement avec python run.py.",
    ], placeholder="captures, extraits de code et diagrammes complémentaires")
    for paragraph in document.paragraphs:
        for run in paragraph.runs:
            run.font.color.rgb = RGBColor(0, 0, 0)
    document.save(OUTPUT)
    print(f"Rapport généré : {OUTPUT}")


if __name__ == "__main__":
    build()
