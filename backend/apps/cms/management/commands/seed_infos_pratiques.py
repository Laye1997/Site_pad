"""Renseigne la rubrique « Infos pratiques » à partir de ce que l'ancien site publiait.

Bilan de l'audit de l'ancien site (19-20/09/2026) :
- Douane, Taxes portuaires, Lexique : contenu repris (le lexique renvoyé par le site est partiel) ;
- Prévisions du trafic et Croisières : tableaux de données -> pages dynamiques du module navires ;
- Lignes régulières : carte interactive (image reprise, détail par continent indisponible) ;
- Formalités, Horaires, Contacts, Accès, Météo : pages en erreur 404 sur l'ancien site ;
- FAQ : texte factice (« lorem ipsum ») -> FAQ recomposée à partir d'informations déjà publiées ;
- Heures de marées : données de test sans valeur -> à brancher sur une source officielle.
Aucune information n'est inventée : ce qui manque est signalé par un encadré « À compléter ».
Ne modifie que les pages vides ; --force réécrit le contenu.
"""

from django.core.management.base import BaseCommand

from apps.cms.management.commands.seed_trafic_passagers import callout, h, image, p, ul
from apps.cms.models import StandardPage
from apps.core.blocks import ContentStreamBlock

NUMERO_VERT = "800 801 802"


def ol(items):
    return {
        "type": "paragraph",
        "value": "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>",
    }


def todo(text):
    return callout("À compléter", text)


def previsions_trafic():
    return [
        p(
            "Les escales prévues, les navires à quai et les départs sont consultables en temps "
            'réel sur la page <a href="/fr/navires/?filtre=arrivees">Mouvement des navires</a>, '
            "avec recherche par navire, port ou consignataire."
        ),
        p(
            "Le calendrier des paquebots est publié sur la page "
            '<a href="/fr/navires/croisieres/">Escales de croisière</a>.'
        ),
    ]


def lignes_regulieres():
    return [
        image(
            "origine/mapppad.jpg",
            "Carte des lignes maritimes régulières au départ de Dakar",
            "Planisphère bleu sur lequel des lignes blanches relient Dakar, point rouge, aux "
            "autres continents.",
        ),
        p(
            "La carte présente les liaisons maritimes régulières qui relient le port de Dakar "
            "aux différents continents."
        ),
        todo(
            "Le détail des lignes régulières par continent (armements, escales, fréquences) est "
            "à fournir par la direction commerciale. L'ancien site l'affichait dans une carte "
            "interactive dont les données n'ont pas pu être récupérées."
        ),
    ]


def formalites():
    return [
        p(
            "Cette rubrique présente les formalités à accomplir pour le passage des marchandises "
            "au port de Dakar."
        ),
        ul(
            [
                '<a href="/fr/infos-pratiques/formalites/douane/">Douane</a> : conditions, '
                "documents, procédure et redevances de dédouanement ;",
                '<a href="/fr/infos-pratiques/formalites/taxes-portuaires/">Taxes portuaires</a> '
                ": redevances applicables aux navires, aux marchandises et à l'occupation du "
                "domaine.",
            ]
        ),
        callout("Une question ?", f"Numéro vert du Port Autonome de Dakar : {NUMERO_VERT}."),
    ]


def douane():
    return [
        h("Conditions à remplir"),
        p(
            "Les opérateurs doivent posséder une carte import-export ou une autorisation "
            "exceptionnelle d'importer avant de dédouaner les marchandises."
        ),
        h("Documents à fournir"),
        ul(
            [
                "Facture commerciale",
                "Facture de fret",
                "Certificat d'origine",
                "Liste de colisage",
                "Autorisation d'importation",
                "Certificat d'assurance",
                "Déclaration préalable d'importation (pour les valeurs égales ou supérieures à "
                "1 000 000 FCFA)",
                "Attestation COTECNA (pour les valeurs F.O.B égales ou supérieures à "
                "3 000 000 FCFA)",
                "Connaissement",
                "Attestation de change",
                "Titres d'exonération",
                "Pour les produits alimentaires et les médicaments : certificats sanitaires et "
                "de qualité spécifiques",
            ]
        ),
        h("Procédure à suivre"),
        p("Le transitaire doit :"),
        ol(
            [
                "établir une note de détail ;",
                "saisir cette note dans le système GAINDE ;",
                "déposer les documents à la Douane ;",
                "régler les redevances au Trésor ;",
                "obtenir le « Bon à enlever » ;",
                "retirer la marchandise.",
            ]
        ),
        h("Redevances à payer"),
        ul(
            [
                "Redevances de débarquement et de magasinage",
                "Timbre douanier",
                "Prélèvement COSEC (0,20 % de la valeur CAF)",
                "Prélèvement communautaire de solidarité",
                "Prestations informatiques",
            ]
        ),
        h("Dédouanement en transit"),
        p(
            "Le dédouanement en transit nécessite une « déclaration d'acquits à caution », "
            "accompagnée de documents spécifiques et d'une caution bancaire."
        ),
        callout("Une question ?", f"Numéro vert du Port Autonome de Dakar : {NUMERO_VERT}."),
    ]


def taxes_portuaires():
    return [
        h("Redevances applicables aux navires pilotables"),
        p(
            "Un navire devient pilotable dès que son volume atteint 1 500 m³. Le volume se "
            "calcule avec la formule <b>V = L × l × Tme</b>, où L est la longueur, l la largeur "
            "maximale et Tme le tirant d'eau maximal d'été."
        ),
        p(
            "Les redevances concernent le pilotage et le balisage, l'amarrage, le désamarrage "
            "et le séjour."
        ),
        h("Redevances applicables aux navires non pilotables"),
        p(
            "Les navires de moins de 1 500 m³ ne sont pas obligatoirement pilotables. Ils "
            "paient une redevance de balisage, d'abri et d'usage du plan d'eau protégé, "
            "calculée selon le même volume V."
        ),
        h("Barème applicable aux marchandises"),
        p(
            "Il concerne les droits de passage des marchandises à l'importation et à "
            "l'exportation, en transit et en transbordement, ainsi que les droits sur les "
            "passagers."
        ),
        h("Redevances d'occupation"),
        p("Elles se répartissent en quatre catégories :"),
        ul(
            [
                "les terre-pleins banalisés ;",
                "les installations non banalisées adjacentes au quai ;",
                "les installations non banalisées non adjacentes au quai ;",
                "les installations situées hors de la barrière douanière.",
            ]
        ),
        p(
            "Les marchandises bénéficient de 7 jours gratuits à l'importation et à "
            "l'exportation sur les terre-pleins banalisés. Au-delà, une majoration de 30 % "
            "s'applique."
        ),
        todo(
            "Les montants détaillés des barèmes (pilotage, marchandises, occupation) sont à "
            "publier par la direction financière : l'ancien site n'en présentait que le principe."
        ),
    ]


LEXIQUE = [
    (
        "Accostage",
        "Manœuvre d'approche finale du navire à l'ouvrage (quai ou appontement) conçu pour "
        "permettre le stationnement des navires, leur amarrage et la manutention.",
    ),
    (
        "Affrètement (remise de navire)",
        "Se distingue du contrat de transport (remise de marchandises). L'affrètement porte sur "
        "l'usage et la jouissance du navire par l'affréteur (le « fréteur » met le navire à "
        "disposition de l'affréteur) ; le contrat de transport porte sur la marchandise que le "
        "chargeur confie au transporteur contre paiement du fret.",
    ),
    (
        "Affréteur",
        "Personne qui loue un navire ou qui exploite un navire en location, selon les termes du "
        "contrat de location ou charte-partie d'affrètement.",
    ),
    (
        "Amarrage",
        "Immobilisation d'un navire au moyen d'aussières (câbles) à un quai ou une bouée.",
    ),
    (
        "Armateur",
        "Personne qui arme un navire en lui fournissant matériel, vivres, combustible, équipage "
        "et tout ce qui est nécessaire à la navigation. Il exploite le navire en son nom, qu'il "
        "soit ou non propriétaire.",
    ),
    ("Arrimage", "Opération qui consiste à fixer solidement les marchandises à bord du navire."),
    (
        "Avitaillement",
        "Fourniture des marchandises, vivres et combustibles nécessaires à bord du navire, pour "
        "le voyage en mer.",
    ),
]


def lexique():
    return [
        p("Les principaux termes du vocabulaire maritime et portuaire."),
        *[item for term, definition in LEXIQUE for item in (h(term, "h3"), p(definition))],
        todo(
            "Le lexique repris de l'ancien site s'arrête à la lettre A : la suite est à fournir "
            "par la direction concernée."
        ),
    ]


def marees():
    return [
        p(
            "À Dakar, la marée est semi-diurne : le niveau de la mer connaît en général deux "
            "pleines mers et deux basses mers par jour. Le marnage est d'environ un mètre "
            "en moyenne, et peut atteindre environ un mètre et demi en vives-eaux."
        ),
        h("Horaires officiels"),
        p(
            "Les heures et les hauteurs de marée du port de Dakar sont calculées par le Service "
            "hydrographique et océanographique de la Marine (SHOM). Consultez les prédictions "
            'officielles sur <a href="https://maree.shom.fr/">maree.shom.fr</a>.'
        ),
        todo(
            "Les données affichées par l'ancien site étaient des valeurs de test. Cette page "
            "affichera les horaires du jour directement dès qu'une source de données (SHOM) sera "
            "raccordée : clé d'accès à demander par le PAD."
        ),
    ]


def meteo():
    return [
        p(
            "Cette rubrique présentera les prévisions météorologiques et l'état de la mer sur la "
            "rade de Dakar."
        ),
        todo(
            "La page météo de l'ancien site n'existe plus. Le choix de la source de données "
            "(service météorologique officiel) est à arrêter par le PAD."
        ),
    ]


def horaires():
    return [
        h("Liaisons maritimes de passagers"),
        ul(
            [
                '<a href="/fr/nos-services/trafic-passagers/dakar-goree/">Dakar-Gorée</a> : '
                "rotations quotidiennes, horaires différents en semaine et le dimanche ;",
                '<a href="/fr/nos-services/trafic-passagers/dakar-ziguinchor/">'
                "Dakar-Ziguinchor</a> : départs de Dakar les mardi, jeudi, vendredi et dimanche "
                "à 20h.",
            ]
        ),
        p(
            "Pour la liaison Dakar-Ziguinchor, l'enregistrement des bagages est possible tous "
            "les jours de 8h30 à 17h."
        ),
        callout("Renseignements", f"Numéro vert du Port Autonome de Dakar : {NUMERO_VERT}."),
        todo("Les horaires d'ouverture des services et des guichets sont à renseigner."),
    ]


def contacts():
    return [
        h("Port Autonome de Dakar"),
        ul(
            [
                "<b>Adresse</b> : Boulevard Abdoulaye Wade, BP 3195 Dakar, Sénégal",
                f"<b>Numéro vert</b> : {NUMERO_VERT}",
                '<b>E-mail</b> : <a href="mailto:contacts@portdakar.sn">contacts@portdakar.sn</a>',
                "<b>Site web</b> : www.portdakar.sn",
                "<b>Réseaux sociaux</b> : @Portautonomededakar (Facebook, X, Instagram, "
                "YouTube, LinkedIn)",
            ]
        ),
        h("Services en ligne"),
        p(
            'Le portail de services est accessible sur <a href="https://atlantis.portdakar.sn">'
            "atlantis.portdakar.sn</a> (connexion et création de compte)."
        ),
        todo(
            "Les contacts par direction et par service (commercial, ressources humaines, "
            "réclamations) sont à renseigner."
        ),
    ]


def acces():
    return [
        p("Le Port Autonome de Dakar est situé Boulevard Abdoulaye Wade, à Dakar (BP 3195)."),
        image(
            "origine/installation_0.jpg",
            "Plan aérien des installations portuaires",
            "Vue aérienne du port de Dakar avec ses môles et ses installations légendés.",
        ),
        p(
            'Voir aussi <a href="/fr/nous-decouvrir/presentation/position-geographique/">'
            'Position géographique</a> et <a href="/fr/nous-decouvrir/presentation/'
            'infrastructures/">Infrastructures</a>.'
        ),
        todo(
            "Les conditions d'accès au port (badges, contrôles, zones réservées) sont à "
            "renseigner par le service sûreté."
        ),
    ]


def faq():
    return [
        p(
            "Les réponses ci-dessous reprennent les informations publiées par le Port Autonome "
            "de Dakar."
        ),
        h("Comment joindre le Port Autonome de Dakar ?", "h3"),
        p(
            f"Par le numéro vert {NUMERO_VERT} ou par e-mail à contacts@portdakar.sn. Toutes "
            'les coordonnées sont sur la page <a href="/fr/infos-pratiques/contacts/">Contacts'
            "</a>."
        ),
        h("Comment obtenir un agrément ?", "h3"),
        p(
            'La liste des pièces à fournir dépend de la profession : voir <a href="/fr/'
            'opportunites-affaires/procedures-agrements/obtenir-un-agrement/">Obtenir un '
            "agrément</a>."
        ),
        h("Où déclarer mon chiffre d'affaires d'agréé ?", "h3"),
        p(
            'Avec le formulaire de votre profession, disponible sur la page <a href="/fr/'
            "opportunites-affaires/procedures-agrements/formulaires-declaration-chiffres-"
            "affaires/\">Formulaires de déclaration de chiffres d'affaires</a>."
        ),
        h("Combien de temps mes marchandises peuvent-elles rester sans frais sur le port ?", "h3"),
        p(
            "Sur les terre-pleins banalisés : 7 jours pour les marchandises conventionnelles et "
            "les véhicules à destination du Sénégal, 20 jours pour les marchandises "
            "conventionnelles en transit et 12 jours pour les véhicules en transit. Détails : "
            '<a href="/fr/nos-services/marchandises/stockage-entreposage/">Stockage / '
            "entreposage</a>."
        ),
        h("Quels sont les horaires de la traversée Dakar-Gorée ?", "h3"),
        p(
            'Ils diffèrent en semaine et le dimanche : voir <a href="/fr/nos-services/'
            'trafic-passagers/dakar-goree/">Dakar-Gorée</a>.'
        ),
        h("Quels bagages puis-je emporter sur la liaison Dakar-Ziguinchor ?", "h3"),
        p(
            "Jusqu'à 200 kg par passager. Les bagages peuvent être enregistrés tous les jours "
            "de 8h30 à 17h."
        ),
        h("Où voir les navires attendus ou à quai ?", "h3"),
        p(
            'Sur la page <a href="/fr/navires/">Mouvement des navires</a>, mise à jour en '
            "continu."
        ),
    ]


PAGES = {
    "previsions-trafic": previsions_trafic,
    "lignes-regulieres": lignes_regulieres,
    "formalites": formalites,
    "douane": douane,
    "taxes-portuaires": taxes_portuaires,
    "lexique": lexique,
    "marees": marees,
    "meteo": meteo,
    "horaires": horaires,
    "contacts": contacts,
    "acces": acces,
    "faq": faq,
}


class Command(BaseCommand):
    help = "Renseigne les pages d'Infos pratiques (contenu de l'ancien site, sans invention)."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Réécrit le contenu existant.")

    def handle(self, *args, force: bool, **options):
        for slug, builder in PAGES.items():
            page = StandardPage.objects.filter(slug=slug).first()
            if page is None:
                self.stdout.write(f"{slug} : page introuvable (lancez seed_site_structure).")
                continue
            if len(page.body) and not force:
                self.stdout.write(f"{page.title} : contenu déjà présent, ignoré.")
                continue
            page.body = ContentStreamBlock().to_python(builder())
            page.save_revision().publish()
            self.stdout.write(f"{page.title} : contenu enregistré.")
