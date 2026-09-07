# Système de Gestion Automatisée des Documents Techniques et Factures (OCR)

Application web Flask permettant d'importer des factures/documents (PDF, image),
d'en extraire automatiquement le texte via OCR (Tesseract), puis d'en extraire
les champs clés (numéro de facture, fournisseur, date, montant).

## 1. Prérequis à installer sur ton PC

### a) Python
Télécharge et installe Python 3.11+ depuis https://www.python.org/downloads/
⚠️ Pendant l'installation Windows, coche bien **"Add Python to PATH"**.

Vérifie ensuite dans un terminal :
```
python --version
```

### b) Visual Studio Code (l'éditeur)
Télécharge-le ici : https://code.visualstudio.com/
Une fois installé, ouvre VS Code puis va dans l'onglet **Extensions** (icône de blocs
à gauche) et installe :
- **Python** (de Microsoft)
- **Pylance** (généralement installée avec)

### c) Tesseract OCR (le moteur de reconnaissance de texte)
C'est un programme séparé de Python, indispensable.

- **Windows** : télécharge l'installeur ici :
  https://github.com/UB-Mannheim/tesseract/wiki
  Installe-le (par défaut dans `C:\Program Files\Tesseract-OCR\`).
  Pense à installer le pack de langue **française** pendant l'installation.

- **Mac** : `brew install tesseract tesseract-lang`

- **Linux (Ubuntu/Debian)** :
  ```
  sudo apt install tesseract-ocr tesseract-ocr-fra
  ```

### d) Poppler (nécessaire pour lire les PDF avec pdf2image)
- **Windows** : télécharge ici https://github.com/oschwartz10612/poppler-windows/releases
  décompresse, et ajoute le dossier `bin` au PATH Windows.
- **Mac** : `brew install poppler`
- **Linux** : `sudo apt install poppler-utils`

## 2. Ouvrir le projet dans VS Code

1. Décompresse le dossier `gestion-factures` reçu quelque part sur ton PC
   (ex: `Documents/gestion-factures`)
2. Ouvre VS Code
3. Menu **Fichier > Ouvrir un dossier...** et sélectionne le dossier `gestion-factures`

## 3. Créer un environnement virtuel (recommandé, isole les dépendances du projet)

Dans VS Code, ouvre un terminal (**Terminal > Nouveau terminal**), puis :

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

Une fois activé, tu dois voir `(venv)` apparaître au début de la ligne du terminal.
VS Code te proposera peut-être aussi de sélectionner cet environnement comme
interpréteur Python par défaut (accepte-le, ou fais Ctrl+Shift+P > "Python: Select Interpreter").

## 4. Installer les dépendances du projet

```bash
pip install -r requirements.txt
```

## 5. (Windows uniquement) Indiquer le chemin de Tesseract

Si Tesseract n'est pas dans le PATH, crée un fichier `.env` à la racine du projet :
```
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## 6. Lancer l'application

```bash
python run.py
```

Tu devrais voir un message du type `Running on http://127.0.0.1:5000`.
Ouvre cette adresse dans ton navigateur : c'est ton application !

## 7. Structure du projet

```
gestion-factures/
├── app/
│   ├── __init__.py       # création de l'application Flask
│   ├── config.py         # configuration (base de données, dossiers...)
│   ├── models.py         # modèle de données "Document"
│   ├── ocr_utils.py      # extraction OCR + parsing des champs de facture
│   ├── routes.py         # toutes les pages/routes du site
│   ├── templates/        # pages HTML
│   ├── static/css/       # styles
│   └── uploads/          # fichiers uploadés stockés ici
├── requirements.txt
├── run.py                # point d'entrée : c'est ce fichier qu'on lance
└── database.db           # généré automatiquement au 1er lancement
```

## 8. Prochaines étapes possibles

- **Authentification** : ajouter Flask-Login pour gérer des comptes utilisateurs
- **Amélioration OCR** : ajuster les expressions régulières dans `ocr_utils.py`
  selon les vrais formats de factures de tes fournisseurs
- **Recherche/filtres** : ajouter une barre de recherche sur le tableau de bord
- **Export** : bouton pour exporter la liste en Excel/CSV
- **Déploiement** : passer de SQLite à PostgreSQL et héberger sur un serveur
  (Render, Railway, PythonAnywhere, ou un VPS de ton entreprise)
- **Traitement asynchrone** : si tu as beaucoup de documents, utiliser Celery
  pour que l'OCR ne bloque pas la page pendant l'upload

## 9. Déployer gratuitement sur Render

Le projet contient un `Dockerfile` et un `render.yaml` prêts pour un service web Render gratuit.

1. Envoie le projet sur un dépôt GitHub privé ou public.
2. Dans Render, choisis **New > Blueprint** et connecte le dépôt.
3. Render détecte `render.yaml` et construit l'image Docker.
4. Renseigne les variables marquées `sync: false` dans les paramètres du service.
5. Ne copie jamais le fichier `.env` dans GitHub.

Le stockage local du plan gratuit peut être supprimé lors d'un redéploiement. Pour conserver
les factures et la base de données, utilise ensuite une base PostgreSQL et un stockage de fichiers persistant.
