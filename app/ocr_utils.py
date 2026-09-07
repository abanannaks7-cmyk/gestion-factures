"""
Module responsable de :
1. Extraire le texte brut d'un document (image ou PDF) via Tesseract OCR
2. Analyser ce texte pour en extraire les champs clés d'une facture
   (numéro, date, montant, fournisseur)

C'est ici que tu pourras affiner les règles au fur et à mesure que tu testes
sur de vraies factures de ton entreprise.
"""

import os
import re
import pytesseract
from PIL import Image


def nettoyer_montant(montant_str):
    if not montant_str:
        return None

    texte = montant_str.replace(" ", "").replace("\u00a0", "").replace(",", ".")
    match = re.search(r"[0-9]+(?:\.[0-9]+)?", texte)
    if not match:
        return None

    try:
        return float(match.group(0))
    except ValueError:
        return None


def classer_document(texte):
    texte = texte.lower()
    if any(keyword in texte for keyword in ["facture", "total ttc", "montant ttc", "invoice"]):
        return "facture"
    if any(keyword in texte for keyword in ["rapport", "maintenance", "controle", "intervention"]):
        return "rapport_maintenance"
    if any(keyword in texte for keyword in ["fiche technique", "caractéristiques", "specifications", "datasheet"]):
        return "doc_technique"
    return "facture"


def identifier_logo_fournisseur(texte, fournisseur=None):
    texte = texte or ""
    fournisseur = fournisseur or ""
    texte_haut = texte.upper()

    patterns = {
        "edf": r"\bEDF\b",
        "engie": r"\bENGIE\b",
        "total": r"\bTOTAL\b",
        "sncf": r"\bSNCF\b",
        "airbus": r"\bAIRBUS\b",
        "orange": r"\bORANGE\b",
        "amazon": r"\bAMAZON\b",
        "apple": r"\bAPPLE\b",
        "societe_abc": r"SOCIETE\s+ABC",
        "stateco": r"\bSTATECO\b",
        "nsie": r"\bNSIE\b",
    }
    for logo_key, regex in patterns.items():
        if re.search(regex, texte_haut):
            return logo_key

    if fournisseur:
        extracted = re.sub(r"[^A-Z0-9]+", "_", fournisseur.upper()).strip("_")
        if extracted:
            return extracted[:20].lower()

    return "fournisseur"


def extraire_texte(chemin_fichier, tesseract_cmd=None, langue="fra+eng+ara"):
    """
    Extrait le texte d'un fichier image (png/jpg) ou PDF via OCR.
    Retourne le texte brut (str).
    """
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    extension = chemin_fichier.rsplit(".", 1)[-1].lower()

    if extension == "pdf":
        from pdf2image import convert_from_path

        pages = convert_from_path(chemin_fichier, dpi=300)
        texte_total = ""
        for page in pages:
            texte_total += pytesseract.image_to_string(page, lang=langue) + "\n"
        return texte_total.strip()

    else:
        image = Image.open(chemin_fichier)
        image = image.convert("L")
        return pytesseract.image_to_string(image, lang=langue).strip()


def extraire_champs_facture(texte):
    """
    Cherche dans le texte OCR des motifs typiques d'une facture française/marocaine.
    Retourne un dict avec les champs trouvés (ou None si non trouvés).

    NOTE : ce sont des règles de départ basées sur des expressions régulières.
    Avec de vraies factures, tu devras ajuster ces patterns selon le format
    de tes fournisseurs. Pour une extraction plus robuste à terme, on pourra
    passer à une librairie de NLP ou à un service OCR spécialisé factures.
    """

    resultat = {
        "numero_facture": None,
        "date_facture": None,
        "montant_ttc": None,
        "fournisseur": None,
        "type_panne": None,
        "duree_maintenance": None,
    }

    # Numéro de facture : ex "Facture N° 2024-00123", "Invoice #12345"
    match = re.search(
        r"(?:facture|invoice)\s*(?:n[°o]?|#)?\s*[:\-]?\s*([A-Z0-9\-/]{2,20})",
        texte,
        re.IGNORECASE,
    )
    if match:
        resultat["numero_facture"] = match.group(1).strip()

    # Date : formats jj/mm/aaaa ou jj-mm-aaaa
    match = re.search(r"\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\b", texte)
    if match:
        resultat["date_facture"] = match.group(1)

    # Montant TTC : ex "Total TTC : 1 250,00 MAD" ou "Total TTC: 1250.00"
    match = re.search(
        r"(?:total\s*ttc|montant\s*ttc|net\s*à\s*payer)\s*[:\-]?\s*([\d\s]+[.,]\d{2})",
        texte,
        re.IGNORECASE,
    )
    if match:
        resultat["montant_ttc"] = match.group(1).strip()

    # Fournisseur : heuristique plus précise
    lignes = [l.strip() for l in texte.split("\n") if l.strip()]
    def ligne_valide_fournisseur(ligne):
        if len(ligne) < 3:
            return False
        if re.search(r"\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}", ligne):
            return False
        if re.search(r"(?:total\s*ttc|montant\s*ttc|net\s*à\s*payer|\d+[.,]\d{2})", ligne, re.IGNORECASE):
            return False
        if re.search(r"\b(?:facture|invoice|date|num|numero|#|n[°o])\b", ligne, re.IGNORECASE):
            return False
        return bool(re.search(r"[A-Za-zÀ-ÖØ-öø-ÿ]", ligne))

    for ligne in lignes:
        if re.search(r"(sarl|sa|sas|limited|ltd|co|company|entreprise|societe|groupe)", ligne, re.IGNORECASE):
            resultat["fournisseur"] = ligne[:255]
            break

    if not resultat["fournisseur"]:
        for ligne in lignes:
            if ligne_valide_fournisseur(ligne):
                resultat["fournisseur"] = ligne[:255]
                break

    if not resultat["fournisseur"] and lignes:
        resultat["fournisseur"] = lignes[0][:255]

    # Informations sémantiques : type de panne et durée de maintenance
    panne_match = re.search(
        r"(?:type\s+de\s+panne|panne|probl[eè]me|d[ée]faillance)\s*[:\-]?\s*([A-Za-z0-9éèêàçûîôœ\s\-]{4,120})",
        texte,
        re.IGNORECASE,
    )
    if panne_match:
        type_panne = panne_match.group(1).strip()
        if len(type_panne) > 3 and not re.search(r"\b(date|facture|montant|total|invoice)\b", type_panne, re.IGNORECASE):
            resultat["type_panne"] = type_panne[:255]

    duree_match = re.search(
        r"(?:dur[eé]e(?:\s+de)?\s+maintenance|maintenance\s+de|intervention\s+de|arr[eê]t\s+de|temps\s+(?:d'|de)\s+(?:r[eé]paration|maintenance))\s*[:\-]?\s*([0-9]+(?:[.,][0-9]+)?\s*(?:h(?:eures?)?|j(?:ours?)?|jours?|minutes?))",
        texte,
        re.IGNORECASE,
    )
    if duree_match:
        resultat["duree_maintenance"] = duree_match.group(1).strip()

    return resultat
