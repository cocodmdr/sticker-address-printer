TRANSLATIONS = {
    "en": {
        "hero_title": "Print address labels in minutes",
        "hero_desc": "Upload your CSV, pick your Avery sheet (or build your own format), tweak margins, preview the result, and export a print-ready PDF for mailing campaigns.",
        "dark_mode": "Dark mode",
        "how_it_works": "How it works",
        "step1_title": "1. Upload",
        "step1_desc": "Import a CSV with title, name, surname, address and country.",
        "step2_title": "2. Configure",
        "step2_desc": "Select Avery format or define your own label sheet dimensions.",
        "step3_title": "3. Print",
        "step3_desc": "Preview labels, generate PDF, and print on sticker sheets.",
        "templates_preview": "Templates preview",
        "generate_labels": "Generate your labels",
        "need_example": "Need an example?",
        "download_sample": "Download sample CSV",
        "preview_labels": "Preview labels",
    },
    "fr": {
        "hero_title": "Imprimez des étiquettes d'adresse en quelques minutes",
        "hero_desc": "Importez votre CSV, choisissez votre planche Avery (ou créez votre propre format), ajustez les marges, prévisualisez le rendu et exportez un PDF prêt à imprimer.",
        "dark_mode": "Mode sombre",
        "how_it_works": "Comment ça marche",
        "step1_title": "1. Import",
        "step1_desc": "Importez un CSV avec civilité, prénom, nom, adresse et pays.",
        "step2_title": "2. Configuration",
        "step2_desc": "Choisissez un format Avery ou définissez votre propre format d'étiquette.",
        "step3_title": "3. Impression",
        "step3_desc": "Prévisualisez les étiquettes, générez le PDF et imprimez.",
        "templates_preview": "Aperçu des modèles",
        "generate_labels": "Générez vos étiquettes",
        "need_example": "Besoin d'un exemple ?",
        "download_sample": "Télécharger un CSV exemple",
        "preview_labels": "Prévisualiser les étiquettes",
    },
    "nl": {
        "hero_title": "Print adreslabels in minuten",
        "hero_desc": "Upload je CSV, kies je Avery-vel (of maak je eigen formaat), pas marges aan, bekijk een preview en exporteer een printklare PDF.",
        "dark_mode": "Donkere modus",
        "how_it_works": "Hoe het werkt",
        "step1_title": "1. Upload",
        "step1_desc": "Importeer een CSV met titel, naam, achternaam, adres en land.",
        "step2_title": "2. Configuratie",
        "step2_desc": "Kies een Avery-formaat of definieer je eigen etiketformaat.",
        "step3_title": "3. Print",
        "step3_desc": "Bekijk labels, genereer PDF en print op je stickervellen.",
        "templates_preview": "Sjabloonvoorbeeld",
        "generate_labels": "Genereer je labels",
        "need_example": "Voorbeeld nodig?",
        "download_sample": "Voorbeeld-CSV downloaden",
        "preview_labels": "Labels previewen",
    },
}


def normalize_lang(value: str | None) -> str:
    v = (value or "en").lower().strip()
    return v if v in TRANSLATIONS else "en"


def t(lang: str, key: str) -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
