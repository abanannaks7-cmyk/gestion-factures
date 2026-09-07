from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import os

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_PATH = os.path.join(BASE, 'rapport_30_pages.docx')

sections = [
    {
        'title': 'Rapport de projet — Application Gestion Factures',
        'paragraphs': [
            'Ce document présente un rapport détaillé de l’application web de gestion automatique des documents techniques et factures. Il explique l’architecture, les fonctionnalités, le traitement OCR, les interfaces, la configuration, les tests et les recommandations futures.',
            'L’objectif est de fournir un dossier complet de 30 pages, conçu pour accompagner une présentation projet, une revue de code ou une documentation métier.',
            'Le rapport inclut la description technique du système, les choix d’implémentation, la structure des données et les flux principaux qui font fonctionner l’application.',
            'Chaque section suivante documente un aspect clé du projet : du démarrage de l’application jusqu’aux points d’amélioration et aux perspectives de déploiement.',
        ],
    },
    {
        'title': 'Contexte et objectifs métier',
        'paragraphs': [
            'L’application vise à centraliser et automatiser le traitement de documents administratifs et techniques, en particulier les factures et documents de maintenance. Elle permet d’importer des fichiers, de réaliser une extraction OCR et d’analyser les données structurées.',
            'Dans un environnement professionnel, ce type de solution réduit le temps de saisie manuel et limite les erreurs humaines lors de la gestion des factures. La logique métier est donc orientée vers la qualité des données extraites et la facilité d’utilisation.',
            'Le site doit proposer des fonctionnalités de consultation simple, une interface claire et une gestion des erreurs transparentes. Il doit également permettre l’export et la recherche rapide, pour suivre l’activité documentaire.',
            'Un autre objectif est de proposer un assistant virtuel pour aider l’utilisateur à trouver des documents ou à expliquer des anomalies sans devoir parcourir le tableau de bord manuellement.',
        ],
    },
    {
        'title': 'Architecture technique générale',
        'paragraphs': [
            'L’application est construite avec Flask, un framework Python léger adapté aux projets web rapides. Flask offre une structure flexible pour la définition des routes, la gestion des templates et l’exécution des traitements backend.',
            'Le projet utilise Flask-SQLAlchemy pour l’accès à la base de données SQLite. Ce choix simplifie le stockage local et la migration rapide en développement, mais peut évoluer vers PostgreSQL ou MySQL en production.',
            'Le moteur OCR est fourni par Tesseract, associé à pytesseract et pdf2image pour la prise en charge des fichiers PDF et images. Ces composants permettent de convertir un fichier scanné en texte brut, qui est ensuite analysé par des expressions régulières.',
            'Côté frontend, l’application s’appuie sur Bootstrap 5 pour assurer un rendu responsive et moderne. La couche CSS personnalisée améliore l’apparence avec un thème sombre et des éléments visuels soignés.',
        ],
    },
    {
        'title': 'Structure de la base de données',
        'paragraphs': [
            'Le modèle principal est Document, qui stocke les métadonnées du fichier, le texte OCR, le statut du traitement et les champs extraits comme le numéro de facture, la date et le montant.',
            'D’autres entités incluent ContactMessage pour les messages du formulaire de contact, User pour les comptes utilisateurs et ComplianceAlert pour les alertes de conformité liées aux documents.',
            'Le schéma est conçu pour être extensible : le modèle Document accepte un logo fournisseur, des informations de panne et une durée de maintenance quand le document est de type rapport technique.',
            'Des colonnes additionnelles sont créées automatiquement par le mécanisme de migration interne, garantissant la compatibilité des anciennes bases avec les évolutions du code.',
        ],
    },
    {
        'title': 'Flux d’importation des documents',
        'paragraphs': [
            'L’importation se fait via la route /upload, accessible depuis le menu de navigation. L’utilisateur peut sélectionner un fichier PDF ou image accepté par le système.',
            'Le fichier est sauvegardé dans le dossier uploads, puis un enregistrement Document est créé en base avec le statut initial "en_attente".',
            'Ensuite, l’OCR est lancé : le texte est extrait du fichier, puis analysé pour identifier les champs clés. Le statut passe à "ok" en cas de succès ou "echec" si l’extraction est insuffisante.',
            'Des alertes de conformité sont ensuite évaluées pour détecter les anomalies de données ou les documents nécessitant une vérification manuelle.',
        ],
    },
    {
        'title': 'Traitement OCR et extraction des données',
        'paragraphs': [
            'Le module ocr_utils.py centralise les fonctions de traitement du texte. Il prend en charge les PDF via pdf2image et les images directes via Pillow.',
            'Le texte extrait est nettoyé puis passé à des patterns qui recherchent le numéro de facture, la date, le montant TTC et le nom du fournisseur.',
            'Une logique supplémentaire tente de reconnaître le type de document et d’identifier un logo fournisseur à partir de mots-clés dans le texte.',
            'Cette architecture facilite l’ajout futur de règles plus avancées ou d’un modèle d’apprentissage pour améliorer l’extraction sur des formats de factures variés.',
        ],
    },
    {
        'title': 'Détails du modèle Document',
        'paragraphs': [
            'Le modèle Document contient des informations essentielles : nom du fichier, chemin, type de document, date d’importation et texte OCR brut.',
            'Il inclut aussi les champs détectés automatiquement : numéro de facture, fournisseur, date de facture, montant TVA comprise, type de panne et durée de maintenance.',
            'Le champ anomalie permet de marquer un document lorsque certains critères de validation sont déclenchés, comme un montant inhabituellement élevé.',
            'Le modèle gère également le logo fournisseur, ce qui permet d’afficher un badge visuel dans le tableau de bord pour une meilleure lisibilité.',
        ],
    },
    {
        'title': 'Interface utilisateur et navigation',
        'paragraphs': [
            'L’interface repose sur une barre de navigation simple offrant l’accès au tableau de bord, à l’import, à la FAQ, au contact et aux pages d’information.',
            'La page d’accueil affiche une vue synthétique avec des statistiques clés et une liste de documents importés, triée par date.',
            'La navigation est responsive grâce à Bootstrap, ce qui rend l’application utilisable sur mobile et tablette.',
            'Un thème clair/sombre est géré par JavaScript et stocké dans localStorage, permettant à l’utilisateur de conserver ses préférences.',
        ],
    },
    {
        'title': 'Tableau de bord et filtres',
        'paragraphs': [
            'Le tableau de bord présente la liste des documents importés et propose des filtres par mot-clé, type de document, statut OCR et intervalle de dates.',
            'Cette fonctionnalité de recherche facilite la localisation d’une facture spécifique ou d’un document technique parmi un volume important.',
            'Des badges visuels indiquent le statut OCR (OK, échec, en attente) pour une lecture rapide des résultats.',
            'Un système de sélection multiple permet ensuite d’exécuter des actions en masse comme l’export ou la suppression.',
        ],
    },
    {
        'title': 'Gestion des documents individuels',
        'paragraphs': [
            'La page de détail d’un document affiche le fichier sélectionné, les informations extraites et le texte OCR brut.',
            'L’utilisateur peut corriger manuellement les champs détectés si l’OCR n’a pas été parfaitement précis.',
            'Un bouton de suppression permet de retirer le document de la base et du stockage, avec une confirmation pour éviter les suppressions accidentelles.',
            'La section de prévisualisation offre un rendu intégré du fichier via une iframe, ce qui aide à consulter le document sans le télécharger.',
        ],
    },
    {
        'title': 'Assistant virtuel et interaction',
        'paragraphs': [
            'L’application inclut un assistant virtuel accessible depuis une fenêtre flottante en bas de l’écran.',
            'Celui-ci peut répondre aux questions sur les documents et guider l’utilisateur dans la recherche de factures ou l’identification d’anomalies.',
            'Lorsque la clé OPENAI_API_KEY est configurée, l’assistant peut utiliser OpenAI pour générer des réponses plus riches ; sinon, il fonctionne en mode local avec des réponses standard.',
            'Cette fonctionnalité enrichit l’expérience utilisateur en proposant une aide contextuelle sans quitter l’interface principale.',
        ],
    },
    {
        'title': 'Gestion des erreurs et retours utilisateur',
        'paragraphs': [
            'Le site affiche des messages de notification pour informer l’utilisateur des succès ou des échecs : import, OCR, suppression, etc.',
            'Ces messages sont gérés via Flash de Flask et se ferment automatiquement après quelques secondes.',
            'En cas d’erreur de traitement OCR, l’application conserve le document et affiche un avertissement clair pour permettre une révision manuelle.',
            'Les logs d’exception sont également consignés côté serveur pour faciliter le diagnostic et la correction des anomalies techniques.',
        ],
    },
    {
        'title': 'Sécurité et authentification',
        'paragraphs': [
            'La protection des pages est assurée par une vérification de session sur chaque route non publique.',
            'Les pages de connexion, inscription et administrateur restent accessibles sans authentification, tandis que les données documentaires sont réservées aux utilisateurs authentifiés.',
            'Le mot de passe utilisateur est haché avant stockage, garantissant que le texte brut n’est jamais enregistré.',
            'Pour renforcer la sécurité future, on peut ajouter Flask-Login, CSRF tokens et des restrictions de rôle plus fines.',
        ],
    },
    {
        'title': 'Configuration du projet',
        'paragraphs': [
            'La configuration est centralisée dans app/config.py et peut être complétée par un fichier .env en développement.',
            'Les variables principales sont la clé secrète, les chemins de dossier, le moteur OCR et la configuration OpenAI.',
            'Le projet utilise SQLite par défaut pour un démarrage rapide sans serveur externe.',
            'Il est toutefois recommandé de migrer vers une base plus robuste en production, comme PostgreSQL ou MySQL, pour gérer un trafic et des volumes plus importants.',
        ],
    },
    {
        'title': 'Installation pas à pas',
        'paragraphs': [
            'La première étape consiste à créer un environnement virtuel Python et à installer les dépendances listées dans requirements.txt.',
            'Ensuite, l’utilisateur doit s’assurer que Tesseract et Poppler sont installés, car ils sont nécessaires pour l’OCR et la lecture des PDF.',
            'Le démarrage se fait avec python run.py, puis l’application est accessible sur http://127.0.0.1:5000.',
            'Ces instructions garantissent une mise en route simple et reproductible sur Windows comme sur macOS ou Linux.',
        ],
    },
    {
        'title': 'Dépendances principales',
        'paragraphs': [
            'Le projet dépend de Flask, Flask-SQLAlchemy et python-dotenv pour la structure web et la configuration.',
            'Pour l’OCR, pytesseract et Pillow sont nécessaires, tandis que pdf2image assure la gestion des fichiers PDF.',
            'OpenAI est optionnel et n’est utilisé que si la clé API est configurée dans l’environnement.',
            'Ces dépendances permettent de combiner traitement de données, interface utilisateur et extraction de texte dans une application cohérente.',
        ],
    },
    {
        'title': 'Détail des routes principales',
        'paragraphs': [
            'La route principale / affiche le tableau de bord et permet l’accès aux filtres et aux actions sur les documents.',
            'La route /upload gère le formulaire d’import et lance le traitement OCR dès l’envoi du fichier.',
            'La route /export permet de télécharger un export CSV de l’ensemble des documents, utile pour l’analyse externe.',
            'La route /assistant/query sert l’assistant virtuel et renvoie une réponse JSON à l’interface utilisateur.',
        ],
    },
    {
        'title': 'Gestion des uploads',
        'paragraphs': [
            'Les fichiers importés sont stockés dans le dossier app/uploads, ce qui facilite la conservation et la réutilisation des documents.',
            'La fonction secure_filename de Werkzeug est utilisée pour éviter les noms de fichiers dangereux.',
            'Le stockage local est pratique pour le développement, mais en production, il est préférable d’utiliser un service comme S3 ou un système de fichiers partagé.',
            'Le dossier d’upload est créé automatiquement si nécessaire, ce qui améliore la résilience de l’application.',
        ],
    },
    {
        'title': 'Web UI : templates et responsive design',
        'paragraphs': [
            'Les templates Jinja reflètent la structure logique du site : base.html contient l’entête, les messages flash et le widget assistant.',
            'Les pages d’accueil, détail et import héritent de cette structure, garantissant une cohérence visuelle et fonctionnelle.',
            'La responsivité est assurée par Bootstrap et des classes utilitaires pour adapter les composants aux écrans larges et mobiles.',
            'Une attention particulière est portée aux états d’erreur, aux formulaires et à l’accessibilité des boutons.',
        ],
    },
    {
        'title': 'Style visuel et expérience utilisateur',
        'paragraphs': [
            'Le CSS personnalisé crée un thème sombre élégant avec des effets de verre, des ombres douces et des animations légères.',
            'Le bouton assistant flotte dans la page et reste accessible sans masquer le contenu principal.',
            'La navigation est conçue pour être simple et intuitive, avec un accès rapide aux pages clés du site.',
            'Des éléments tels que les badges, les tableaux et les cartes rendent l’interface plus lisible et agréable à utiliser.',
        ],
    },
    {
        'title': 'Comportement du formulaire d’import',
        'paragraphs': [
            'Le formulaire d’import propose un champ de sélection de fichier et des options de type de document et de langue OCR.',
            'Il réalise des vérifications côté serveur pour vérifier que le fichier est autorisé avant de le sauvegarder.',
            'En cas d’erreur, l’utilisateur reçoit un message explicite pour corriger le problème.',
            'Ce procédé garantit que seuls les fichiers valides sont traités et que l’application ne plante pas lors de l’import.',
        ],
    },
    {
        'title': 'Processus d’analyse sémantique',
        'paragraphs': [
            'Après OCR brut, le texte est analysé pour extraire des valeurs structurées grâce à des expressions régulières.',
            'Le système détecte les informations typiques d’une facture, mais il est aussi capable d’identifier des éléments de maintenance ou de documentation technique.',
            'Les règles sont explicites et faciles à ajuster, ce qui permet d’adapter le traitement aux formats réels rencontrés.',
            'Cette approche reste flexible, car elle peut être complétée ultérieurement par un module de machine learning.',
        ],
    },
    {
        'title': 'Liste des fichiers clés du projet',
        'paragraphs': [
            'Le cœur du projet se trouve dans le dossier app, avec routes.py, models.py, ocr_utils.py et templates/.',
            'Le fichier run.py lance l’application via create_app, tandis que requirements.txt liste les dépendances Python.',
            'Le README fournit les instructions d’installation et de mise en route pour tout nouvel utilisateur.',
            'Le projet est organisé pour séparer la logique métier, l’accès aux données et l’interface, favorisant la maintenance.',
        ],
    },
    {
        'title': 'Annexes techniques',
        'paragraphs': [
            'Une annexe peut décrire les expressions régulières utilisées pour extraire les informations des factures.',
            'Une autre annexe présente la structure HTML des templates et les classes CSS personnalisées majeures.',
            'Ces informations aident un développeur à comprendre rapidement comment étendre le projet.',
            'Elles constituent une ressource précieuse pour documenter les choix de conception et de développement.',
        ],
    },
    {
        'title': 'Tests et validation',
        'paragraphs': [
            'L’application inclut des tests automatisés qui vérifient les routes principales et le bon fonctionnement du traitement.',
            'Les tests permettent de s’assurer que les modifications ultérieures n’introduisent pas de régressions.',
            'La commande de validation est python -m unittest tests.test_app -v, ce qui exécute l’ensemble des tests disponibles.',
            'Ces tests sont essentiels pour garantir la stabilité du projet lors de nouvelles évolutions.',
        ],
    },
    {
        'title': 'Déploiement et environnement local',
        'paragraphs': [
            'Pour déployer le projet localement, il est recommandé de configurer un environnement virtuel et de vérifier la présence de Tesseract et Poppler.',
            'En production, il faudra envisager un serveur web comme Gunicorn ou Uvicorn devant Nginx, ainsi qu’une base de données plus robuste.',
            'L’utilisation d’un fichier .env permet de séparer les secrets et les paramètres d’environnement du code source.',
            'Ce type de déploiement est compatible avec de nombreux hébergeurs Python modernes.',
        ],
    },
    {
        'title': 'Points d’amélioration immédiats',
        'paragraphs': [
            'Ajouter un système de pagination côté backend pour les listes de documents volumineuses.',
            'Intégrer PDF.js pour une prévisualisation plus fiable et complète des documents PDF.',
            'Ajouter des tests unitaires supplémentaires pour couvrir les fonctions d’extraction OCR et les routes bulk.',
            'Améliorer l’authentification avec Flask-Login et des rôles utilisateur plus fins.',
        ],
    },
    {
        'title': 'Suggestions pour évoluer vers une version entreprise',
        'paragraphs': [
            'Migrer la base de données vers PostgreSQL pour une meilleure scalabilité et performance.',
            'Ajouter un stockage objet pour les uploads, comme Amazon S3 ou Azure Blob Storage.',
            'Mettre en place un traitement asynchrone des fichiers avec Celery ou RQ pour les volumes élevés.',
            'Prévoir un tableau de bord d’analyse plus riche avec des graphiques et des KPI métier.',
        ],
    },
    {
        'title': 'Conformité et qualité des données',
        'paragraphs': [
            'Les alertes de conformité permettent de signaler les documents dont les montants ou informations semblent incorrects.',
            'Ce mécanisme peut être enrichi avec des règles métier propre à une entreprise.',
            'La qualité des données est primordiale pour garantir des rapports et des exports fiables.',
            'Un suivi des anomalies facilite la révision manuelle des documents problématiques.',
        ],
    },
    {
        'title': 'Expérience utilisateur recommandée',
        'paragraphs': [
            'Assurer un retour utilisateur clair à chaque action, en particulier lors des imports et des suppressions.',
            'Proposer des indications précises sur les erreurs d’OCR et les documents non exploitables.',
            'Offrir un mode sombre/clair pour répondre aux préférences de différents utilisateurs.',
            'Prévoir une page d’aide ou une FAQ directement intégrée pour diminuer les demandes de support.',
        ],
    },
    {
        'title': 'Maintenance et évolutions futures',
        'paragraphs': [
            'Documenter les conventions de code et la structure du projet pour faciliter la prise en main par de nouveaux développeurs.',
            'Planifier des revues régulières des règles d’extraction OCR en fonction des nouveaux formats de documents rencontrés.',
            'Mettre en place un suivi des versions et des migrations de base de données pour sécuriser les évolutions.',
            'Préparer une feuille de route pour l’ajout de nouvelles fonctionnalités métier.',
        ],
    },
    {
        'title': 'Annexe : liste des fichiers importants',
        'paragraphs': [
            'app/__init__.py : initialisation de l’application et création de la base de données.',
            'app/config.py : configuration des chemins, des clés et des paramètres du projet.',
            'app/models.py : définition des tables Document, User, ContactMessage et ComplianceAlert.',
            'app/ocr_utils.py : traitement OCR, nettoyage et extraction des champs factures.',
        ],
    },
    {
        'title': 'Annexe : structure des templates',
        'paragraphs': [
            'base.html : template de base incluant la navigation, les messages flash et l’assistant.',
            'index.html : tableau de bord principal avec la liste des documents et les filtres.',
            'detail.html : vue détaillée du document et formulaire de correction des champs extraits.',
            'upload.html : formulaire d’import de documents.',
        ],
    },
    {
        'title': 'Annexe : flux de données',
        'paragraphs': [
            'Le flux commence par l’import du fichier, qui est enregistré dans uploads et créé en base.',
            'L’OCR est ensuite exécuté pour produire un texte brut et des champs extraits.',
            'Le résultat est stocké dans la base de données et affiché dans le tableau de bord.',
            'Enfin, des exports CSV et des actions en masse permettent de traiter les documents à grande échelle.',
        ],
    },
    {
        'title': 'Synthèse finale et conclusion',
        'paragraphs': [
            'Ce rapport présente une vue complète de l’application de gestion de documents et de factures.',
            'Il met en évidence les choix techniques, les fonctionnalités clés et les pistes d’évolution pour renforcer la solution.',
            'Le projet est prêt à être enrichi avec des fonctionnalités d’entreprise : utilisateurs, déploiement cloud, dashboards avancés et traitement asynchrone.',
            'Cette documentation doit servir de base pour la maintenance, l’expertise métier et la communication auprès des parties prenantes.',
        ],
    },
]


def add_title_page(doc, title, subtitle):
    para = doc.add_paragraph()
    run = para.add_run(title)
    run.bold = True
    run.font.size = Pt(28)
    para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    para = doc.add_paragraph()
    run = para.add_run(subtitle)
    run.italic = True
    run.font.size = Pt(14)
    para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    doc.add_paragraph()
    doc.add_paragraph('Auteur : Équipe de développement NovaDoc OCR').alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    doc.add_paragraph('Date : 27 juillet 2026').alignment = WD_PARAGRAPH_ALIGNMENT.CENTER


if __name__ == '__main__':
    doc = Document()
    add_title_page(doc, 'Rapport de projet - Application Gestion Factures', 'Rapport Word détaillé 30 pages')
    for index, section in enumerate(sections[1:], start=2):
        doc.add_page_break()
        heading = doc.add_heading(section['title'], level=1)
        heading.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        for paragraph in section['paragraphs']:
            p = doc.add_paragraph(paragraph)
            p.paragraph_format.space_after = Pt(10)
            p.runs[0].font.size = Pt(11)

        if index == 5:
            table = doc.add_table(rows=1, cols=2)
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = 'Fichier'
            hdr_cells[1].text = 'Description'
            data = [
                ('app/routes.py', 'Routes principales et logique serveur'),
                ('app/models.py', 'Définition des modèles de données'),
                ('app/ocr_utils.py', 'Extraction OCR et parsing'),
                ('app/templates/base.html', 'Structure de la page et assistant'),
            ]
            for name, desc in data:
                row_cells = table.add_row().cells
                row_cells[0].text = name
                row_cells[1].text = desc
            table.style = 'Light Shading Accent 1'
    doc.save(OUTPUT_PATH)
    print('Saved', OUTPUT_PATH)
