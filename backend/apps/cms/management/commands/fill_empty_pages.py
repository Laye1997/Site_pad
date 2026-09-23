"""Remplit les pages vides de l'arborescence avec le contenu de l'ancien site portdakar.sn.

Idempotent : une page qui a déjà du contenu n'est jamais écrasée (sauf --force).
Usage :  python manage.py fill_empty_pages [--force]
"""

from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from wagtail.documents.models import Document
from wagtail.models import Page

from apps.cms.models import Partner

PDF_DIR = (
    Path(settings.BASE_DIR) / "sources" / "portdakar-documents-pdf" / "sites" / "default" / "files"
)
EMAIL = "pad-serviceclient@portdakar.sn"


def p(text):
    return ("paragraph", f"<p>{text}</p>")


def h(text):
    return ("heading", {"text": text, "level": "h2"})


def ul(*items):
    return ("paragraph", "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>")


def table(headers, rows):
    return ("table", {"headers": headers, "rows": rows})


def callout(title, body):
    return ("callout", {"title": title, "body": body})


def cta(label, url):
    return ("cta", {"label": label, "url": url})


# slug -> (module, corps). Les slugs sont uniques dans l'arborescence.
CONTENT = {
    "nous-decouvrir": (
        "subpages",
        [p("Histoire, organisation, chiffres et partenaires : tout savoir sur le port de Dakar.")],
    ),
    "presentation": (
        "subpages",
        [
            p(
                "Le Port Autonome de Dakar est le premier port en eau profonde d'Afrique de "
                "l'Ouest pour les navires venant du nord. Découvrez sa position, son histoire, "
                "ses infrastructures et son organisation."
            )
        ],
    ),
    "position-geographique": (
        "",
        [
            p(
                "Le Port de Dakar bénéficie d'une localisation stratégique à la pointe occidentale "
                "de l'Afrique, au carrefour des grandes lignes maritimes reliant l'Europe à "
                "l'Amérique du Sud et l'Amérique du Nord à l'Afrique du Sud."
            ),
            p(
                "Premier accès en eau profonde pour les navires venant du nord et dernier port "
                "accessible en remontant du sud, il offre un gain de navigation de deux à trois "
                "jours par rapport aux autres ports de la côte ouest-africaine."
            ),
            h("Un plan d'eau protégé"),
            ul(
                "Chenal d'accès dragué à 13,5 m",
                "Cercle d'évitage de 500 m de diamètre",
                "Dix kilomètres de linéaire de quai",
                "Marées comprises entre 0,20 m et 1,80 m",
                "Accès direct permanent et services 24 h/24",
            ),
        ],
    ),
    "historique": (
        "",
        [
            table(
                ["Année", "Événement"],
                [
                    ["1857", "Création : escale maritime de Dakar (ligne France–Brésil)."],
                    ["1864", "Édification des phares (Mamelles 1864, Cap-Manuel 1866)."],
                    [
                        "1910",
                        "Raccordements routiers et ferroviaires, hangars, grues, remorqueurs.",
                    ],
                    [
                        "1926",
                        "Construction des môles 5, 6 et 8, postes pétroliers de la jetée Nord.",
                    ],
                    ["1933", "Édification du môle 3, hangars et nouveaux dragages."],
                    ["1945", "Môle 4 (1947-1951) et wharf pétrolier (1954)."],
                    ["1962", "Premier quai de pêche, suivi d'un second en 1972."],
                    ["1980", "Construction du môle de pêche."],
                    [
                        "1985",
                        "Terminal à conteneurs : deux postes à quai, huit hectares.",
                    ],
                    ["1987", "Changement de statut : création du Port Autonome de Dakar."],
                    ["2009", "Installation de deux portiques de quai Panamax par DP World."],
                    ["2010", "Inauguration de la gare maritime internationale."],
                    [
                        "2013",
                        "Parrainage des installations portuaires aux noms de figures nationales.",
                    ],
                ],
            )
        ],
    ),
    "infrastructures": (
        "",
        [
            p(
                "Port maritime en eaux profondes situé par 14° 40′ de latitude nord et 17° 25′ de "
                "longitude ouest, Dakar est à l'intersection des grandes routes de la côte "
                "ouest-africaine."
            ),
            h("Zone Nord"),
            p(
                "Quatre môles, un terminal vraquier (Necotrans), un terminal à conteneurs exploité "
                "par DP World (environ 300 000 EVP par an) et une zone hydrocarbures."
            ),
            h("Zone Sud"),
            p(
                "Trois môles pour les marchandises diverses et conteneurs, le môle 3 pour le "
                "trafic malien, un terminal roulier et la gare maritime internationale."
            ),
            h("Installations connexes"),
            ul(
                "Port de pêche Seydina Limamou Laye : deux kilomètres de quai",
                "Dakarnave : le plus grand chantier naval de la côte ouest-africaine",
                "Plateforme de distribution aménagée sur 21 hectares",
            ),
        ],
    ),
    "organisation": (
        "subpages",
        [p("Statut, gouvernance et organigramme.")],
    ),
    "statut-et-mission": (
        "",
        [
            p(
                "Depuis le 1er juillet 1987, le Port Autonome de Dakar est une société nationale "
                "au capital de 52 milliards de FCFA, en vertu de la loi n° 87-28 du 18 août 1987 "
                "modifiée."
            ),
            h("Missions"),
            ul(
                "Exploitation et entretien du port maritime de Dakar et de ses dépendances, "
                "gestion de son domaine mobilier et immobilier",
                "Acquisition et exploitation d'établissements similaires",
                "Participation dans des sociétés commerciales",
                "Opérations commerciales, industrielles, mobilières, immobilières ou financières "
                "liées à son objet",
            ),
        ],
    ),
    "administration": (
        "",
        [
            h("Conseil d'administration"),
            p(
                "La société est administrée par un conseil de 12 membres au plus (Présidence, "
                "Primature, ministères de tutelle et des finances, personnel, secteurs portuaires "
                "et commerciaux). Il délibère sur le plan stratégique, le budget, le patrimoine "
                "et les tarifs portuaires."
            ),
            h("Comité de direction"),
            p(
                "Il assure le contrôle permanent de la gestion entre les réunions du Conseil. "
                "Présidé par le président du Conseil ou un vice-président, il réunit des "
                "représentants des ministères de tutelle et trois membres élus par le Conseil."
            ),
            h("Directeur Général"),
            p(
                "Il assure la gestion générale de la société et veille à l'exécution des "
                "décisions des organes délibérants."
            ),
        ],
    ),
    "assemblee-generale": (
        "",
        [
            h("Composition"),
            p(
                "17 membres votants (Présidence, Primature, ministères techniques et financiers, "
                "personnel, chambres de commerce, entreprises portuaires, représentants maliens, "
                "autorités militaires et judiciaires) et six membres à voix consultative, dont le "
                "Contrôleur financier et le Directeur Général."
            ),
            h("Assemblée générale ordinaire"),
            ul(
                "Examine les rapports de gestion et approuve les comptes",
                "Nomme les commissaires aux comptes",
                "Approuve les conventions réglementées",
            ),
            h("Assemblée générale extraordinaire"),
            p(
                "Elle délibère sur toute modification du capital ou des statuts, sous la "
                "présidence du Président du Conseil d'administration."
            ),
        ],
    ),
    "organigramme": (
        "",
        [
            table(
                ["Structure", "Responsable"],
                [
                    ["Direction Générale", "Doune Pathé MBENGUE, Directeur Général"],
                    ["Secrétariat Général", "Mactar DIALLO"],
                    ["Cellule Audit et Contrôle interne", "Alioune FALL"],
                    ["Cellule Contrôle de gestion", "Khady DIOP"],
                    ["Cellule Communication", "Bineta DIOP"],
                    ["Cellule Qualité, Sécurité, Sûreté, Environnement", "Rokhaya LY"],
                    ["Direction de la Stratégie et des Partenariats", "Momar Ngary BA"],
                    ["Direction Technique", "Ousseynou NDIAYE"],
                    ["Direction de l'Exploitation / Haut Commandement", "Ibrahima DIAW"],
                    ["Direction Commerciale", "Pape Ibrahima SOW"],
                    ["Direction Financière et Comptable", "Babacar NIANG"],
                    ["Direction du Capital Humain", "Mandoye NDOYE"],
                    ["Direction du Digital", "Pape Mass DIALLO"],
                    ["Port de Ziguinchor", "Coumba Diouf NIANG"],
                    ["Port de Kaolack", "Abdoulaye SOGUE"],
                    ["Port de Ndakhonga-Foundiougne", "Ngor DIONE"],
                    ["Port de Saint-Louis", "El Hadji Ndiogou SY"],
                ],
            )
        ],
    ),
    "representation-commerciale": (
        "",
        [
            p(
                "Le PAD a ouvert une représentation commerciale à Bamako pour se rapprocher de "
                "ses partenaires de l'hinterland, mieux écouter les clients maliens et faire de "
                "Dakar la porte naturelle de l'hinterland et le port de référence de l'espace "
                "UEMOA."
            ),
            p(
                "Des avantages infrastructurels et tarifaires spécifiques sont proposés aux "
                "partenaires et clients maliens."
            ),
            callout("Contact", "Numéro vert : 800 801 802"),
        ],
    ),
    "nos-chiffres-cles": (
        "key_figures",
        [p("Les principaux indicateurs d'activité du Port Autonome de Dakar.")],
    ),
    "visiter-le-port": (
        "subpages",
        [
            p(
                "Le PAD organise des visites guidées pour les professionnels et les écoles "
                "spécialisées en commerce international, transport et logistique. Depuis "
                "l'application du code ISPS, l'accès au port est réglementé."
            )
        ],
    ),
    "demande-de-visite": (
        "",
        [
            h("Procédure"),
            ul(
                "Télécharger et remplir le formulaire de demande de visite",
                "Le transmettre 15 jours au moins à l'avance à la Direction Générale",
                "Groupe limité à 35 personnes",
            ),
            h("Informations demandées"),
            p("Nom et prénom, adresse, téléphone, e-mail, structure, motif de la visite."),
            cta("Envoyer ma demande par e-mail", f"mailto:{EMAIL}"),
        ],
    ),
    "visite-virtuelle": (
        "",
        [
            p(
                "La visite virtuelle des installations est en cours de modernisation. En "
                "attendant, découvrez les infrastructures ou organisez une visite guidée."
            ),
            cta(
                "Découvrir les infrastructures", "/fr/nous-decouvrir/presentation/infrastructures/"
            ),
            cta("Demander une visite", "/fr/nous-decouvrir/visiter-le-port/demande-de-visite/"),
        ],
    ),
    "nos-partenaires": (
        "subpages",
        [p("Les entreprises, institutions et ports avec lesquels le PAD travaille au quotidien.")],
    ),
    "partenaires-strategiques": (
        "partners:strategique",
        [p("Opérateurs et industriels au cœur de la chaîne logistique portuaire.")],
    ),
    "partenaires-institutionnels": (
        "partners:institutionnel",
        [p("Administrations, organismes publics et représentants des usagers.")],
    ),
    "partenaires-internationaux": (
        "partners:international",
        [p("Ports jumelés et partenaires à l'international.")],
    ),
    "associations": (
        "",
        [
            table(
                ["Association", "Adresse", "Contact"],
                [
                    [
                        "Union culturelle et sportive des travailleurs du PAD (UCSTPAD)",
                        "Centre culturel Papa Bakary Ndiaye « Béchar », rond-point Cyrnos",
                        "Tél/Fax : 33 848 66 22",
                    ],
                    [
                        "Amicale des cadres du PAD",
                        "21 bd de la Libération, BP 3195 Dakar",
                        "Tél : 33 849 45 45",
                    ],
                    [
                        "Amicale des femmes employées du PAD",
                        "21 bd de la Libération, BP 3195 Dakar",
                        "Tél : 33 849 45 45",
                    ],
                    [
                        "Amicale des jeunes du PAD",
                        "21 bd de la Libération, BP 3195 Dakar",
                        "Tél : 33 849 45 45",
                    ],
                ],
            )
        ],
    ),
    # --- Services ---
    "accueil-navires": (
        "subpages",
        [
            p(
                "Accès nautique, pilotage, remorquage, lamanage, avitaillement et réparation "
                "navale : l'ensemble des services offerts aux navires, 24 h/24."
            )
        ],
    ),
    "pilotage": (
        "",
        [
            p(
                "Le pilotage est l'une des activités à plus forte valeur ajoutée du PAD ; il est "
                "certifié ISO 9001 depuis 2009."
            ),
            callout("Obligation", "Tout navire de plus de 1 500 m³ doit être piloté au PAD."),
            h("Moyens"),
            ul(
                "15 pilotes capitaines au long cours",
                "6 pilotines",
                "7 postes d'amarrage",
                "Vedettes de servitude : délégations, service portuaire, rondes de sécurisation",
            ),
            p(
                "Au terminal de Mbao, les connexions et déconnexions sont assurées par vedette "
                "de servitude."
            ),
        ],
    ),
    "remorquage": (
        "",
        [
            p(
                "Le remorquage est facultatif à Dakar grâce à des conditions nautiques "
                "exceptionnelles. Il est assuré par une entreprise privée certifiée ISO "
                "exploitant cinq remorqueurs, équipés pour la lutte contre la pollution et "
                "l'incendie."
            )
        ],
    ),
    "lamanage": (
        "",
        [
            p(
                "Le lamanage consiste à amarrer et désamarrer les navires à tous les postes, à "
                "l'arrivée, au départ ou lors d'un déhalage."
            ),
            callout("Disponibilité", "Service assuré par le port 24 h/24 et 7 j/7."),
        ],
    ),
    "avitaillement": (
        "",
        [
            h("Eau douce"),
            table(
                ["Zone", "Bouches à quai"],
                [["Nord", "42"], ["Sud", "32"], ["Pêche", "58"], ["Total", "132"]],
            ),
            p(
                "En rade, l'avitaillement se fait par citernes flottantes de 220 à 400 tonnes "
                "(100 m³/h) ou par barge. La qualité de l'eau est contrôlée par l'Institut "
                "Pasteur."
            ),
            h("Hydrocarbures"),
            p(
                "213 bouches réparties sur 10 postes : 250 t/h par navire, "
                "jusqu'à 1 000 t/h par poste."
            ),
        ],
    ),
    "reparation-navale": (
        "",
        [
            p("Dakarnave est l'un des plus grands chantiers navals de la côte ouest-africaine."),
            table(
                ["Équipement", "Caractéristiques"],
                [
                    ["Dock flottant", "235 m × 38 m, capacité de levage 28 000 t"],
                    ["Bassin de radoub", "191 m × 25 m"],
                    ["Quai de réparation", "500 m, tirant d'eau max. 9 m"],
                    ["Syncrolift", "4 plates-formes de 60 m, 1 200 t"],
                ],
            ),
            p("Trois autres slipways privés complètent l'offre de réparation et de carénage."),
            cta("Site de Dakarnave", "https://www.dakarnave.com/"),
        ],
    ),
    "entreprises-agreees": (
        "",
        [
            p("Le PAD agrée les professionnels qui interviennent dans la chaîne portuaire :"),
            ul(
                "Transporteurs de conteneurs",
                "Transitaires",
                "Manutentionnaires",
                "Consignataires",
                "Prestataires de services",
                "Remorqueurs",
                "Shipchandlers",
            ),
            p("La liste à jour des entreprises agréées est consultable sur le portail de service."),
            cta("Accéder au portail Atlantis", "https://atlantis.portdakar.sn"),
            cta(
                "Obtenir un agrément",
                "/fr/opportunites-affaires/procedures-agrements/obtenir-un-agrement/",
            ),
        ],
    ),
    # --- Opportunités ---
    "opportunites-affaires": (
        "subpages",
        [p("Appels d'offres, avis d'attribution, agréments et plan de passation du PAD.")],
    ),
    "appels-offres": ("marches:appel_offres", [p("Consultations en cours et dossiers associés.")]),
    "avis-attribution": (
        "marches:avis_attribution",
        [p("Résultats des consultations lancées par le PAD.")],
    ),
    "plan-passation": (
        "marches:plan_passation",
        [p("Prévisions annuelles de passation des marchés.")],
    ),
    "manifestation-interet": (
        "marches:manifestation_interet",
        [p("Avis de manifestation d'intérêt en cours.")],
    ),
    # --- Média ---
    "actualites": ("articles:actualite", [p("L'actualité du port et de ses partenaires.")]),
    "communiques-presse": (
        "articles:communique",
        [p("Communiqués officiels du Port Autonome de Dakar.")],
    ),
    "phototheque": ("articles:photos", [p("Photos des événements et des installations du port.")]),
    "videotheque": (
        "articles:photos",
        [p("Vidéos du port et de ses événements ; la vidéothèque sera enrichie prochainement.")],
    ),
    "publications": ("subpages", [p("Rapports et magazine interne « Tam Tam du Docker ».")]),
    "engagements": (
        "subpages",
        [p("Qualité, sécurité, sûreté, environnement et responsabilité sociétale.")],
    ),
    "infos-pratiques": (
        "subpages",
        [p("Prévisions, marées, météo, formalités, horaires et contacts utiles.")],
    ),
    "espace-pro-recrutement": (
        "",
        [
            p(
                "Accédez aux services en ligne du port, déposez votre candidature ou adressez "
                "une réclamation."
            ),
            h("Espace professionnel"),
            p("Connexion ou création de compte sur le portail de service Atlantis."),
            cta("Se connecter au portail Atlantis", "https://atlantis.portdakar.sn"),
            cta("Espace pro du site", "/fr/espace-pro/"),
            h("Carrières"),
            p("Consultez nos offres ci-dessous ou envoyez une candidature spontanée."),
            cta("Candidature spontanée", "/fr/recrutement/postuler/"),
            h("Réclamation client"),
            p(f"Écrivez-nous à {EMAIL} ou appelez le numéro vert 800 801 802."),
        ],
    ),
}

PARTNER_CATEGORIES = {
    "strategique": [
        "Maersk",
        "Bolloré Logistics",
        "GETMA",
        "Grimaldi Group",
        "DP World",
        "Necotrans",
        "SNTT Logistics",
        "Vivo Energy",
        "Sococim",
        "Ciments du Sahel",
        "Grands Moulins de Dakar",
        "ICS",
        "SAR",
    ],
    "institutionnel": [
        "Senelec",
        "SDE",
        "Sonatel",
        "La Poste",
        "Douane sénégalaise",
        "ANAM",
        "APIX",
        "CNP",
        "ONES",
        "CCIAD",
        "UNACOIS Jappo",
        "FENAGIE Pêche",
        "Chambre des notaires du Sénégal",
        "Ministère de l'Industrie et du Commerce",
        "Ministère de l'Intérieur et de la Sécurité publique",
    ],
    "international": [
        "Port de Dunkerque",
        "Autorità di Sistema Portuale de Gênes",
        "Puertos de Las Palmas",
        "PortMiami",
        "Port of South Louisiana",
        "Port du Cap",
        "Port de l'Amitié",
    ],
}

# slug -> (libellé, fichiers PDF) : documents publiés en téléchargement direct
PUBLICATIONS = {
    "tam-tam-du-docker": (
        "Tam Tam du Docker",
        [
            "ttdd_ndeg10_der.pdf",
            "ttdd_ndeg11_.pdf",
            "ttdd_ndeg17.pdf",
            "ttdd_ndeg18_1.pdf",
            "magazine_ttdd_ndeg19_ok_3.pdf",
            "magazine_ttdd_ndeg23_v8.pdf",
            "tam-tam_du_docker_num2ro_24_1.pdf",
        ],
    ),
    "rapport": ("Rapport", ["rapport_statistiques_2021_synthese_compressed_compressed.pdf"]),
}


def import_document(filename):
    path = PDF_DIR / filename
    if not path.exists():
        return None
    title = filename.rsplit(".", 1)[0].replace("_", " ").replace("ndeg", "n°").strip().capitalize()
    doc = Document.objects.filter(title=title).first()
    if doc is None:
        doc = Document(title=title)
        with path.open("rb") as handle:
            doc.file.save(filename, File(handle), save=False)
        doc.save()
    return doc


class Command(BaseCommand):
    help = "Remplit les pages vides avec le contenu de l'ancien site (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Écrase les pages déjà remplies.")

    def handle(self, *args, force=False, **options):
        filled = 0
        for slug, (module, body) in CONTENT.items():
            for page in Page.objects.filter(slug=slug).exclude(depth__lte=2):
                filled += self._fill(page.specific, module, body, force)
        for slug, (label, files) in PUBLICATIONS.items():
            page = Page.objects.filter(slug=slug).first()
            docs = [d for d in (import_document(f) for f in files) if d]
            if page and docs:
                links = [f'<a id="{d.id}" linktype="document">{d.title}</a>' for d in docs]
                body = [p(f"{label} : documents à télécharger."), ul(*links)]
                filled += self._fill(page.specific, "", body, force)
        cruise = Page.objects.filter(slug="croisieres").first()
        if cruise and not any(b.block_type == "cta" for b in cruise.specific.body):
            cruise = cruise.specific
            cruise.body.append(
                (
                    "cta",
                    {"label": "Voir le calendrier des escales", "url": "/fr/navires/croisieres/"},
                )
            )
            cruise.save_revision().publish()
            filled += 1
        classified = 0
        for category, names in PARTNER_CATEGORIES.items():
            classified += Partner.objects.filter(name__in=names, category="").update(
                category=category
            )
        self.stdout.write(f"{filled} page(s) remplie(s), {classified} partenaire(s) classé(s).")

    @staticmethod
    def _fill(page, module, body, force):
        if not hasattr(page, "body"):
            return 0
        if len(page.body) and not force:
            # une page déjà rédigée garde son contenu ; seul le module manquant est activé
            if module and hasattr(page, "module") and not page.module:
                page.module = module
                page.save_revision().publish()
                return 1
            return 0
        page.body = body
        if hasattr(page, "module"):
            page.module = module
        page.save_revision().publish()
        return 1
