import csv
import io
import os
import re
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage
from functools import wraps
from openai import OpenAI, OpenAIError
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app, jsonify, Response, session,
    send_from_directory
)
from sqlalchemy import or_, func
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

from .models import db, Document, ContactMessage, User, ComplianceAlert
from .ocr_utils import (
    extraire_texte, extraire_champs_facture,
    nettoyer_montant, classer_document,
    identifier_logo_fournisseur,
)

main_bp = Blueprint("main", __name__)


@main_bp.before_request
def require_authentication():
    if request.path.startswith("/static/"):
        return None

    public_paths = {"/login", "/signup", "/logout", "/admin/login", "/admin/logout", "/assistant/query"}
    public_endpoints = {"main.login", "main.signup", "main.logout", "main.admin_login", "main.admin_logout", "main.assistant_query", "main.set_language"}

    if session.get("admin_authenticated") or session.get("user_id"):
        return None

    if request.path in public_paths or request.endpoint in public_endpoints:
        return None

    if request.endpoint == "static":
        return None

    flash("Veuillez vous connecter pour utiliser le site.", "warning")
    return redirect(url_for("main.login", next=request.path))


def extension_autorisee(nom_fichier):
    return (
        "." in nom_fichier
        and nom_fichier.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


@main_bp.route("/set-language/<language>")
def set_language(language):
    if language in {"fr", "en"}:
        session["language"] = language
    destination = request.args.get("next", "/")
    if not destination.startswith("/") or destination.startswith("//"):
        destination = "/"
    return redirect(destination)


@main_bp.route("/")
def accueil():
    """Tableau de bord : liste de tous les documents traités."""
    recherche = request.args.get("recherche", "", type=str).strip()
    type_document = request.args.get("type_document", "", type=str)
    statut_ocr = request.args.get("statut_ocr", "", type=str)
    filtre_anomalie = request.args.get("anomalie", "", type=str)
    date_debut = request.args.get("date_debut", "", type=str)
    date_fin = request.args.get("date_fin", "", type=str)
    page = max(1, request.args.get("page", 1, type=int))
    per_page = 10

    query = Document.query
    if recherche:
        mot = f"%{recherche}%"
        query = query.filter(
            or_(
                Document.nom_fichier.ilike(mot),
                Document.numero_facture.ilike(mot),
                Document.fournisseur.ilike(mot),
                Document.montant_ttc.ilike(mot),
            )
        )
    if type_document:
        query = query.filter_by(type_document=type_document)
    if statut_ocr:
        query = query.filter_by(statut_ocr=statut_ocr)
    if filtre_anomalie == "1":
        query = query.filter_by(anomalie=True)

    if date_debut:
        try:
            debut = datetime.strptime(date_debut, "%Y-%m-%d")
            query = query.filter(Document.date_upload >= debut)
        except ValueError:
            pass
    if date_fin:
        try:
            fin = datetime.strptime(date_fin, "%Y-%m-%d")
            query = query.filter(Document.date_upload <= fin)
        except ValueError:
            pass

    total = query.count()
    en_attente = query.filter_by(statut_ocr="en_attente").count()
    ok = query.filter_by(statut_ocr="ok").count()
    anomalies = query.filter_by(anomalie=True).count()
    pages = max(1, (total + per_page - 1) // per_page)
    page = min(page, pages)
    documents = (
        query.order_by(Document.date_upload.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return render_template(
        "index.html",
        documents=documents,
        total=total,
        en_attente=en_attente,
        ok=ok,
        anomalies=anomalies,
        recherche=recherche,
        filtre_type=type_document,
        filtre_statut=statut_ocr,
        filtre_anomalie=filtre_anomalie,
        date_debut=date_debut,
        date_fin=date_fin,
        page=page,
        pages=pages,
    )


@main_bp.route("/export")
def export_documents():
    documents = Document.query.order_by(Document.date_upload.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Fichier", "Type", "N° Facture", "Fournisseur",
        "Date facture", "Montant TTC", "Statut OCR", "Anomalie",
        "Importé le", "Langue OCR"
    ])
    for doc in documents:
        writer.writerow([
            doc.nom_fichier,
            doc.type_document,
            doc.numero_facture or "",
            doc.fournisseur or "",
            doc.date_facture or "",
            doc.montant_ttc or "",
            doc.statut_ocr,
            "Oui" if getattr(doc, "anomalie", False) else "Non",
            doc.date_upload.strftime("%d/%m/%Y %H:%M"),
            doc.langue or "",
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=documents_export.csv"},
    )


@main_bp.route("/upload", methods=["GET", "POST"])
def upload():
    """Formulaire d'upload + traitement OCR immédiat."""
    if request.method == "POST":
        if "fichier" not in request.files:
            flash("Aucun fichier sélectionné.", "danger")
            return redirect(request.url)

        fichier = request.files["fichier"]

        if fichier.filename == "":
            flash("Aucun fichier sélectionné.", "danger")
            return redirect(request.url)

        if fichier and extension_autorisee(fichier.filename):
            if not os.path.exists(current_app.config["UPLOAD_FOLDER"]):
                os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)
            nom_securise = secure_filename(fichier.filename)
            chemin = os.path.join(current_app.config["UPLOAD_FOLDER"], nom_securise)
            fichier.save(chemin)

            langue = request.form.get("langue", current_app.config["OCR_LANGUAGES"])
            doc = Document(
                nom_fichier=nom_securise,
                chemin_fichier=chemin,
                type_document=request.form.get("type_document", "facture").strip() or "facture",
                statut_ocr="en_attente",
                langue=langue,
            )
            db.session.add(doc)
            db.session.commit()

            try:
                texte = extraire_texte(
                    chemin,
                    tesseract_cmd=current_app.config["TESSERACT_CMD"],
                    langue=langue,
                )
                champs = extraire_champs_facture(texte)
                doc.type_document = classer_document(texte)

                doc.texte_ocr = texte
                doc.numero_facture = champs["numero_facture"]
                doc.date_facture = champs["date_facture"]
                doc.montant_ttc = champs["montant_ttc"]
                doc.fournisseur = champs["fournisseur"]
                doc.type_panne = champs.get("type_panne")
                doc.duree_maintenance = champs.get("duree_maintenance")
                doc.fournisseur_logo = identifier_logo_fournisseur(texte, doc.fournisseur)
                doc.statut_ocr = "ok" if texte else "echec"

                montant = nettoyer_montant(champs["montant_ttc"])
                moyenne = None
                if montant is not None:
                    moyenne_result = db.session.query(func.avg(Document.montant_ttc.cast(db.Float))).filter(Document.montant_ttc != None).first()
                    if moyenne_result:
                        moyenne = moyenne_result[0]
                doc.anomalie = False
                doc.anomalie_raison = None
                if montant is not None and moyenne is not None and moyenne > 0 and montant > moyenne * 4:
                    doc.anomalie = True
                    doc.anomalie_raison = "Montant inhabituel détecté"
            except Exception as e:
                doc.statut_ocr = "echec"
                doc.anomalie = False
                flash(f"Erreur lors de l'OCR : {e}", "warning")

            db.session.commit()
            # Lancer les vérifications de conformité après le commit pour disposer de l'ID
            try:
                _run_compliance_checks(doc)
            except Exception as e:
                current_app.logger.exception('Erreur lors des vérifications de conformité: %s', e)
            if doc.statut_ocr == "ok":
                flash("Document importé et traité avec succès.", "success")
            else:
                flash("Le document a été enregistré, mais l'OCR n'a pas pu extraire de contenu exploitable.", "warning")
            return redirect(url_for("main.detail", doc_id=doc.id))

        flash("Format de fichier non autorisé (pdf, png, jpg uniquement).", "danger")

    return render_template("upload.html")


@main_bp.route("/assistant/query", methods=["POST"])
def assistant_query():
    payload = request.get_json(silent=True) or {}
    question = payload.get("message", "").strip()
    answer, error = _assistant_repond(question)
    return jsonify({
        "answer": answer,
        "error": error if error and not answer else None,
        "ia_enabled": bool(current_app.config.get("OPENAI_API_KEY")),
    })


def _assistant_repond(message):
    if not message or not message.strip():
        return (
            "Salut ! Pose-moi une question, par exemple : trouve une facture par numéro, explique une anomalie, ou recherche un fournisseur.",
            None,
        )

    if current_app.config.get("OPENAI_API_KEY"):
        return _assistant_ia_repond(message)

    return _assistant_local_repond(message), None


def _assistant_ia_repond(message):
    client = OpenAI(api_key=current_app.config.get("OPENAI_API_KEY"))
    model = current_app.config.get("OPENAI_MODEL", "gpt-3.5-turbo")
    prompt = (
        "Tu es un assistant de gestion de factures. Réponds en français de manière claire et concise. "
        "Tu dois aider à retrouver des factures, expliquer des anomalies et fournir des informations utiles sur les documents. "
        "Si l'utilisateur pose une question sur un document ou un fournisseur, donne une réponse concise et polie."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.5,
            max_tokens=300,
        )
        current_app.logger.debug(f"OpenAI raw response: {response}")
        output_text = None
        if hasattr(response, "choices") and response.choices:
            first_choice = response.choices[0]
            if hasattr(first_choice, "message"):
                output_text = first_choice.message.get("content")
            elif hasattr(first_choice, "text"):
                output_text = first_choice.text

        return output_text or "Désolé, je n'ai pas pu générer de réponse.", None
    except OpenAIError as exc:
        current_app.logger.warning(f"OpenAI error: {exc}. Utilisation du mode local.")
        return _assistant_local_repond(message), None
    except Exception as exc:
        current_app.logger.warning(f"Assistant IA inattendu: {exc}. Utilisation du mode local.")
        return _assistant_local_repond(message), None


def _assistant_local_repond(message):
    texte = message.lower()
    if "anomalie" in texte:
        anomalies = Document.query.filter_by(anomalie=True).order_by(Document.date_upload.desc()).limit(5).all()
        if anomalies:
            lignes = [f"- {d.numero_facture or d.nom_fichier} ({d.fournisseur or 'fournisseur inconnu'}) : {d.anomalie_raison or 'anomalie détectée'}" for d in anomalies]
            return "Voici les anomalies récentes :\n" + "\n".join(lignes)
        return "Je n'ai pas trouvé d'anomalie pour le moment."

    match_num = re.search(r"(?:n[°o]?\s*[:#]?\s*)?([A-Z0-9\-/]{3,20})", message, re.IGNORECASE)
    if "facture" in texte and match_num:
        numero = match_num.group(1)
        documents = Document.query.filter(Document.numero_facture.ilike(f"%{numero}%"))
        docs = documents.all()
        if docs:
            return "Facture trouvée :\n" + "\n".join(
                [f"{d.numero_facture} - {d.fournisseur or 'fournisseur inconnu'} - {d.date_upload.strftime('%d/%m/%Y')}" for d in docs]
            )
        return "Aucun document ne correspond à ce numéro."

    if "fournisseur" in texte or "client" in texte or "entreprise" in texte:
        match = re.search(r"fournisseur\s*[:\-]?\s*([\w\s]+)", texte)
        recherche = None
        if match:
            recherche = match.group(1).strip()
        else:
            elements = re.findall(r"[a-zA-Z0-9]{3,}", texte)
            if elements:
                recherche = elements[-1]
        if recherche:
            documents = Document.query.filter(Document.fournisseur.ilike(f"%{recherche}%"))
            docs = documents.all()
            if docs:
                return "Documents pour ce fournisseur :\n" + "\n".join(
                    [f"{d.numero_facture or d.nom_fichier} - {d.date_facture or '-'} - {d.statut_ocr.upper()}" for d in docs]
                )
            return "Aucun document trouvé pour ce fournisseur."

    if any(keyword in texte for keyword in ["trouve", "cherche", "recherche", "liste", "document"]):
        docs = Document.query.order_by(Document.date_upload.desc()).limit(5).all()
        if docs:
            return "Voici les derniers documents importés :\n" + "\n".join(
                [f"{d.numero_facture or d.nom_fichier} - {d.fournisseur or 'Fournisseur inconnu'} - {d.statut_ocr.upper()}" for d in docs]
            )
        return "Aucun document n'a encore été importé."

    return (
        "Je peux t'aider à retrouver un document par numéro, fournisseur ou expliquer une anomalie."
        " Essaie : ‘Trouve la facture 2024-00123’ ou ‘Qu'est-ce que l'anomalie ?’"
)


def _send_contact_email(msg):
    cfg = current_app.config
    host = cfg.get('SMTP_HOST')
    if not host:
        current_app.logger.info('SMTP non configuré, e-mail de contact non envoyé.')
        return False
    port = cfg.get('SMTP_PORT', 587)
    user = cfg.get('SMTP_USER')
    password = cfg.get('SMTP_PASS')
    from_addr = cfg.get('EMAIL_FROM') or user or 'no-reply@example.com'
    to_addr = from_addr
    subject = f"Nouveau message contact: {msg.sujet or 'Sans sujet'}"
    body = f"Nom: {msg.nom}\nEmail: {msg.email}\nSujet: {msg.sujet}\n\n{msg.message}\n\nDate: {msg.date_created}"
    email_message = EmailMessage()
    email_message["From"] = from_addr
    email_message["To"] = to_addr
    email_message["Reply-To"] = msg.email
    email_message["Subject"] = subject
    email_message.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=10) as server:
        server.ehlo()
        if port != 465:
            try:
                server.starttls(context=context)
                server.ehlo()
            except Exception:
                pass
        if user and password:
            server.login(user, password)
        server.send_message(email_message)
    return True


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('main.admin_login', next=request.path))
        return f(*args, **kwargs)
    return decorated


@main_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('Veuillez renseigner un nom d’utilisateur, un email et un mot de passe.', 'danger')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return render_template('signup.html')

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Ce nom d’utilisateur ou cet email est déjà utilisé.', 'danger')
            return render_template('signup.html')

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        session['username'] = user.username
        flash('Compte créé avec succès. Vous êtes connecté.', 'success')
        next_page = request.args.get('next') or request.form.get('next') or url_for('main.accueil')
        return redirect(next_page)

    return render_template('signup.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Connexion réussie.', 'success')
            next_page = request.args.get('next') or request.form.get('next') or url_for('main.accueil')
            return redirect(next_page)

        flash('Identifiants incorrects.', 'danger')

    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    session.clear()
    flash('Déconnecté.', 'info')
    return redirect(url_for('main.accueil'))


@main_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if (
            username == current_app.config.get('ADMIN_USER')
            and password == current_app.config.get('ADMIN_PASS')
        ):
            session['admin_authenticated'] = True
            flash('Connecté en tant qu\'administrateur.', 'success')
            nxt = request.args.get('next') or url_for('main.admin_contacts')
            return redirect(nxt)
        flash('Identifiants incorrects.', 'danger')
    return render_template('admin_login.html')


@main_bp.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Déconnecté.', 'info')
    return redirect(url_for('main.accueil'))


@main_bp.errorhandler(RequestEntityTooLarge)
def handle_request_entity_too_large(error):
    flash("Le fichier est trop volumineux. Veuillez choisir un fichier de moins de 16 Mo.", "danger")
    return redirect(url_for("main.upload"))


@main_bp.route("/document/<int:doc_id>")
def detail(doc_id):
    """Affiche le détail d'un document + champs extraits, éditables."""
    doc = Document.query.get_or_404(doc_id)
    return render_template("detail.html", doc=doc)


@main_bp.route("/document/<int:doc_id>/modifier", methods=["POST"])
def modifier(doc_id):
    """Permet de corriger manuellement les champs extraits par l'OCR."""
    doc = Document.query.get_or_404(doc_id)
    doc.numero_facture = request.form.get("numero_facture")
    doc.fournisseur = request.form.get("fournisseur")
    doc.date_facture = request.form.get("date_facture")
    doc.montant_ttc = request.form.get("montant_ttc")
    doc.type_panne = request.form.get("type_panne")
    doc.duree_maintenance = request.form.get("duree_maintenance")
    db.session.commit()
    flash("Document mis à jour.", "success")
    return redirect(url_for("main.detail", doc_id=doc.id))


@main_bp.route("/document/<int:doc_id>/supprimer", methods=["POST"])
def supprimer(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if os.path.exists(doc.chemin_fichier):
        os.remove(doc.chemin_fichier)
    # Supprimer d'abord les alertes de conformité liées (évite erreurs FK)
    try:
        ComplianceAlert.query.filter_by(document_id=doc.id).delete()
    except Exception:
        current_app.logger.exception('Impossible de supprimer les alertes liées au document %s', doc.id)

    db.session.delete(doc)
    db.session.commit()
    flash("Document supprimé.", "info")
    return redirect(url_for("main.accueil"))


@main_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # Sert les fichiers uploadés de façon sûre
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@main_bp.route('/documents/bulk_delete', methods=['POST'])
def documents_bulk_delete():
    ids = request.form.getlist('selected_ids')
    if not ids:
        flash('Aucun document sélectionné.', 'warning')
        return redirect(url_for('main.accueil'))
    for doc_id in ids:
        try:
            doc = Document.query.get(int(doc_id))
            if not doc:
                continue
            # delete related alerts
            try:
                ComplianceAlert.query.filter_by(document_id=doc.id).delete()
            except Exception:
                current_app.logger.exception('Erreur suppression alertes pour doc %s', doc.id)
            # remove file
            if os.path.exists(doc.chemin_fichier):
                try:
                    os.remove(doc.chemin_fichier)
                except Exception:
                    current_app.logger.exception('Impossible de supprimer le fichier %s', doc.chemin_fichier)
            db.session.delete(doc)
        except Exception:
            current_app.logger.exception('Erreur lors de la suppression en masse pour id %s', doc_id)
    db.session.commit()
    flash(f'{len(ids)} document(s) supprimé(s).', 'info')
    return redirect(url_for('main.accueil'))


@main_bp.route('/documents/bulk_export', methods=['POST'])
def documents_bulk_export():
    ids = request.form.getlist('selected_ids')
    if not ids:
        flash('Aucun document sélectionné pour l\'export.', 'warning')
        return redirect(url_for('main.accueil'))
    documents = Document.query.filter(Document.id.in_([int(i) for i in ids])).order_by(Document.date_upload.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Fichier", "Type", "N° Facture", "Fournisseur",
        "Date facture", "Montant TTC", "Statut OCR", "Anomalie",
        "Importé le", "Langue OCR"
    ])
    for doc in documents:
        writer.writerow([
            doc.nom_fichier,
            doc.type_document,
            doc.numero_facture or "",
            doc.fournisseur or "",
            doc.date_facture or "",
            doc.montant_ttc or "",
            doc.statut_ocr,
            "Oui" if getattr(doc, "anomalie", False) else "Non",
            doc.date_upload.strftime("%d/%m/%Y %H:%M"),
            doc.langue or "",
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=documents_selected_export.csv"},
    )


@main_bp.route("/api/documents")
def api_documents():
    """Petite API JSON, utile si tu veux brancher un frontend séparé plus tard."""
    documents = Document.query.order_by(Document.date_upload.desc()).all()
    return jsonify([d.to_dict() for d in documents])


@main_bp.route('/faq')
def faq():
    faqs = [
        {"q": "Quels formats de fichiers sont supportés ?", "a": "PDF, PNG et JPG sont supportés."},
        {"q": "Quelle langue est supportée par l'OCR ?", "a": "Plusieurs langues ; par défaut : français et anglais. Tu peux changer via le formulaire d'upload."},
        {"q": "Comment corriger un champ extrait par l'OCR ?", "a": "Ouvre le détail d'un document et modifie les champs, puis enregistre."},
    ]
    return render_template('faq.html', faqs=faqs)


@main_bp.route('/apropos')
def apropos():
    return render_template('about.html')


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        nom = request.form.get('nom', '').strip()
        email = request.form.get('email', '').strip()
        sujet = request.form.get('sujet', '').strip()
        message = request.form.get('message', '').strip()

        if not nom or not email or not message:
            flash('Veuillez renseigner au minimum le nom, l’email et le message.', 'danger')
            return redirect(url_for('main.contact'))
        if (
            len(nom) > 120
            or len(email) > 254
            or len(sujet) > 200
            or len(message) > 5000
            or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email)
        ):
            flash('Vérifiez les champs du formulaire et leurs longueurs.', 'danger')
            return redirect(url_for('main.contact'))

        msg = ContactMessage(nom=nom, email=email, sujet=sujet, message=message)
        db.session.add(msg)
        db.session.commit()

        # Envoi d'un email de notification si SMTP configuré
        try:
            if _send_contact_email(msg):
                flash('Merci, votre message a été envoyé. Nous vous répondrons rapidement.', 'success')
            else:
                flash('Message enregistré. La notification par e-mail n’est pas configurée.', 'warning')
        except Exception as e:
            current_app.logger.exception('Erreur envoi email contact: %s', e)
            flash('Message enregistré mais l\'envoi de notification par e-mail a échoué.', 'warning')

        return redirect(url_for('main.contact'))

    return render_template('contact.html')


def _run_compliance_checks(doc: Document):
    """Applique des règles de conformité basiques et crée des alerts si besoin."""
    issues = []

    # Règle: numéro de facture présent
    if not doc.numero_facture:
        issues.append(('missing_invoice_number', 'error', "Numéro de facture manquant"))

    # Règle: fournisseur présent
    if not doc.fournisseur:
        issues.append(('missing_supplier', 'error', "Fournisseur manquant"))

    # Règle: date présente et pas dans le futur
    if not doc.date_facture:
        issues.append(('missing_invoice_date', 'error', "Date de facture manquante"))
    else:
        try:
            d = datetime.strptime(doc.date_facture, '%d/%m/%Y')
            if d > datetime.utcnow():
                issues.append(('future_invoice_date', 'warning', "Date de facture dans le futur"))
        except Exception:
            # si format inconnu, avertir
            issues.append(('bad_date_format', 'warning', "Format de date non standard"))

    # Règle: montant > 0
    try:
        montant_val = float(doc.montant_ttc.replace(',', '.')) if doc.montant_ttc else 0
        if montant_val <= 0:
            issues.append(('invalid_amount', 'error', "Montant invalide ou nul"))
    except Exception:
        issues.append(('bad_amount_format', 'warning', "Format du montant non standard"))

    # Règle : type de panne / durée de maintenance contextualisés pour les rapports de maintenance
    if doc.type_document == 'rapport_maintenance' and not doc.type_panne:
        issues.append(('missing_failure_type', 'warning', "Type de panne non détecté"))
    if doc.type_document == 'rapport_maintenance' and not doc.duree_maintenance:
        issues.append(('missing_maintenance_duration', 'warning', "Durée de maintenance non détectée"))

    # Règle : référence de facture inhabituelle ou suspecte
    if doc.type_document == 'facture' and doc.numero_facture:
        reference_pattern = re.compile(r"[A-Z0-9\-/]{5,}", re.IGNORECASE)
        if not reference_pattern.match(doc.numero_facture):
            issues.append(('invalid_invoice_reference', 'warning', "Référence de facture inhabituelle ou inexistante"))

        duplicate = Document.query.filter(
            Document.numero_facture == doc.numero_facture,
            Document.id != doc.id,
        ).first()
        if duplicate:
            issues.append(('duplicate_invoice_reference', 'warning', "Référence de facture déjà existante"))
    elif doc.type_document == 'facture' and not doc.numero_facture:
        issues.append(('missing_invoice_reference', 'error', "Référence de facture manquante"))

    # Règle: OCR status ok
    if doc.statut_ocr != 'ok':
        issues.append(('ocr_failed', 'warning', "OCR non concluant"))

    # Créer les alertes en base
    for key, level, message in issues:
        # Eviter les doublons exacts pour le même document
        exists = ComplianceAlert.query.filter_by(document_id=doc.id, rule_key=key, message=message, resolved=False).first()
        if not exists:
            alert = ComplianceAlert(document_id=doc.id, rule_key=key, level=level, message=message)
            db.session.add(alert)
            db.session.commit()
            # Envoi d'email d'alerte si configuré
            try:
                _send_alert_email(alert)
            except Exception:
                current_app.logger.exception('Echec envoi email d alerte')


def _send_alert_email(alert: ComplianceAlert):
    cfg = current_app.config
    host = cfg.get('SMTP_HOST')
    if not host:
        current_app.logger.info('SMTP non configuré, alerte non envoyée pour le document %s.', alert.document_id)
        return False
    port = cfg.get('SMTP_PORT', 587)
    user = cfg.get('SMTP_USER')
    password = cfg.get('SMTP_PASS')
    from_addr = cfg.get('EMAIL_FROM') or user or 'no-reply@example.com'
    to_addr = from_addr
    subject = f"Alerte conformité: document #{alert.document_id}"
    body = f"Document ID: {alert.document_id}\nNiveau: {alert.level}\nRègle: {alert.rule_key}\nMessage: {alert.message}\nDate: {alert.date_created}\n"
    email_message = EmailMessage()
    email_message["From"] = from_addr
    email_message["To"] = to_addr
    email_message["Subject"] = subject
    email_message.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=10) as server:
        server.ehlo()
        if port != 465:
            try:
                server.starttls(context=context)
                server.ehlo()
            except Exception:
                pass
        if user and password:
            server.login(user, password)
        server.send_message(email_message)



@main_bp.route('/admin/contacts')
@admin_required
def admin_contacts():
    messages = ContactMessage.query.order_by(ContactMessage.date_created.desc()).all()
    return render_template('admin_contacts.html', messages=messages)


@main_bp.route('/admin/alerts')
@admin_required
def admin_alerts():
    alerts = ComplianceAlert.query.order_by(ComplianceAlert.date_created.desc()).all()
    return render_template('admin_alerts.html', alerts=alerts)


@main_bp.route('/admin/alerts/<int:alert_id>/resolve', methods=['POST'])
@admin_required
def admin_alerts_resolve(alert_id):
    alert = ComplianceAlert.query.get_or_404(alert_id)
    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    db.session.commit()
    flash('Alerte marquée comme résolue.', 'success')
    return redirect(url_for('main.admin_alerts'))


@main_bp.route('/admin/alerts/export')
@admin_required
def admin_alerts_export():
    alerts = ComplianceAlert.query.order_by(ComplianceAlert.date_created.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Document ID', 'Rule', 'Level', 'Message', 'Resolved'])
    for a in alerts:
        writer.writerow([a.date_created.strftime('%d/%m/%Y %H:%M'), a.document_id, a.rule_key, a.level, a.message, 'Oui' if a.resolved else 'Non'])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=alerts_export.csv'})


@main_bp.route('/admin/contacts/export')
@admin_required
def admin_contacts_export():
    messages = ContactMessage.query.order_by(ContactMessage.date_created.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Nom", "Email", "Sujet", "Message"])
    for m in messages:
        writer.writerow([m.date_created.strftime("%d/%m/%Y %H:%M"), m.nom, m.email, m.sujet or "", m.message])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=contact_messages.csv"},
    )


@main_bp.route('/admin/contacts/<int:msg_id>/supprimer', methods=['POST'])
@admin_required
def admin_contacts_delete(msg_id):
    msg = ContactMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    flash('Message supprimé.', 'info')
    return redirect(url_for('main.admin_contacts'))
