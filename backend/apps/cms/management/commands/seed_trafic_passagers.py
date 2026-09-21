"""Renseigne la rubrique « Trafic passagers » et ses 4 sous-pages, reprises de l'ancien site.

Sources : pages portdakar.sn (Dakar-Gorée, Dakar-Ziguinchor) et affiche « Politique sûreté GMID ».
Par défaut, ne modifie que les pages dont le contenu est vide ; --force réécrit le contenu.
Les textes marqués « à vérifier » dans l'aide de la commande doivent être relus par le PAD.
"""

from django.core.management.base import BaseCommand

from apps.cms.home_blocks import library_image_id
from apps.core.blocks import ContentStreamBlock
from apps.services.models import ServicePage

SECTION_SLUG = "trafic-passagers"
NUMERO_VERT = "800 801 802"


def h(text, level="h2"):
    return {"type": "heading", "value": {"text": text, "level": level}}


def p(html):
    return {"type": "paragraph", "value": f"<p>{html}</p>"}


def ul(items):
    return {
        "type": "paragraph",
        "value": "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>",
    }


def table(headers, rows):
    return {"type": "table", "value": {"headers": headers, "rows": rows}}


def callout(title, body):
    return {"type": "callout", "value": {"title": title, "body": body}}


def image(static_name, title, alt, caption=""):
    return {
        "type": "image",
        "value": {"image": library_image_id(static_name, title), "caption": caption, "alt": alt},
    }


def contact():
    return callout(
        "Renseignements",
        f"Numéro vert du Port Autonome de Dakar : {NUMERO_VERT}. "
        "Contacts complets : rubrique « Infos pratiques ».",
    )


def trafic_passagers():
    return (
        "Liaisons maritimes et accueil des passagers.",
        [
            p(
                "Le Port Autonome de Dakar assure le transport de passagers, depuis la Gare "
                "Maritime Internationale de Dakar (GMID), à destination de l'île de Gorée et de "
                "Ziguinchor."
            ),
            p(
                "Retrouvez dans cette rubrique la présentation de la gare maritime, les horaires "
                "et les tarifs des liaisons Dakar-Gorée et Dakar-Ziguinchor, ainsi que la "
                "politique de sûreté de la GMID."
            ),
            contact(),
        ],
    )


def gare_maritime():
    return (
        "La Gare Maritime Internationale de Dakar (GMID), point de départ des liaisons "
        "vers Gorée et Ziguinchor.",
        [
            image(
                "origine/banniere-gare-maritime.jpg",
                "Bannière de la gare maritime",
                "Bannière de la Gare Maritime Internationale de Dakar.",
            ),
            p(
                "La Gare Maritime Internationale de Dakar (GMID) est l'installation portuaire "
                "dédiée au transport de passagers et de marchandises à destination de Gorée et "
                "de Ziguinchor."
            ),
            p(
                "Ses services aux passagers et aux marchandises sont certifiés ISO 14001:2015, "
                "ISO 9001:2015 et ISO 45001:2018."
            ),
            h("Liaisons desservies"),
            ul(
                [
                    "Dakar-Ziguinchor : traversées régulières de nuit, horaires et tarifs sur la "
                    "page dédiée ;",
                    "Dakar-Gorée : rotations quotidiennes, horaires et tarifs sur la page dédiée.",
                ]
            ),
            contact(),
        ],
    )


def dakar_goree():
    en_semaine = [
        ["06h15", "06h45"],
        ["07h30", "08h00"],
        ["10h00", "10h30"],
        ["11h00", "12h00"],
        ["12h30", "14h00"],
        ["14h30", "15h00"],
        ["16h00", "16h30"],
        ["17h00 sauf samedi", "18h00 sauf samedi"],
        ["18h30", "19h00"],
        ["20h00", "20h30"],
        ["22h30", "23h00"],
        ["23h30 le vendredi", "00h00 le vendredi"],
        ["00h45 le samedi", "01h15 le samedi"],
    ]
    dimanche = [
        ["07h00", "07h30"],
        ["09h00", "09h30"],
        ["10h00", "10h30"],
        ["12h00", "12h30"],
        ["14h00", "14h30"],
        ["16h00", "16h30"],
        ["17h00", "17h30"],
        ["18h30", "19h00"],
        ["19h30", "20h00"],
        ["20h30", "21h00"],
        ["22h30", "23h00"],
        [
            "23h30 (dimanche et veille de jours fériés)",
            "00h00 (dimanche et veille de jours fériés)",
        ],
    ]
    tarifs = [
        ["Carte de séjour", "15 500 F CFA"],
        ["Groupe scolaire primaire", "400 F CFA"],
        ["Groupe scolaire secondaire", "1 200 F CFA"],
        ["Non-résident Afrique, adulte", "6 000 F CFA"],
        ["Non-résident Afrique, enfant", "3 000 F CFA"],
        ["Résident sénégalais, adulte", "1 500 F CFA"],
        ["Résident sénégalais, enfant", "500 F CFA"],
        ["Résident Afrique, adulte", "3 500 F CFA"],
        ["Résident Afrique, enfant", "2 000 F CFA"],
    ]
    return (
        "La liaison maritime Dakar-Gorée : service public de transport vers l'île de Gorée.",
        [
            image(
                "origine/dakargoree_0.jpg",
                "Vue aérienne de l'île de Gorée",
                "Vue aérienne de l'île de Gorée, avec son embarcadère et une chaloupe qui s'en "
                "approche.",
            ),
            p(
                "La Liaison Maritime Dakar-Gorée est un service public de transport mis en place "
                "par l'État du Sénégal, dont la gestion est confiée à la Société Nationale du "
                "Port Autonome de Dakar (SONAPAD) suivant la convention n° 0174 du 17 octobre "
                "1973."
            ),
            p(
                "Elle est chargée, sous l'autorité exclusive du Directeur Général du Port "
                "Autonome de Dakar, d'assurer avec les chaloupes ou tout autre moyen adéquat mis "
                "à disposition, la desserte de l'île de Gorée, dans les conditions de sécurité "
                "requises."
            ),
            h("Objectifs"),
            ul(
                [
                    "suivre l'entretien des navires conformément à la réglementation de sécurité ;",
                    "assurer la continuité du service par des rotations ponctuelles ;",
                    "fidéliser la clientèle ;",
                    "accompagner la promotion de Gorée, site du patrimoine mondial de l'UNESCO.",
                ]
            ),
            h("Horaires de la traversée"),
            h("En semaine", "h3"),
            table(["Départ de Dakar", "Départ de Gorée"], en_semaine),
            h("Dimanche et jours fériés", "h3"),
            table(["Départ de Dakar", "Départ de Gorée"], dimanche),
            h("Tarifs applicables à la traversée Dakar-Gorée"),
            table(["Type de billet", "Montant de la traversée"], tarifs),
            p(
                "<b>Chaloupe spéciale</b> : moins de 150 passagers, 1 500 000 F CFA ; plus de 150 "
                "passagers, 1 750 000 F CFA. Pour une prise en charge au niveau du môle 3, un "
                "frais supplémentaire de 250 000 F CFA est à payer."
            ),
            image(
                "origine/crea_tarifs_lmdg_plan_de_travail_1-1.png",
                "Affiche des tarifs Dakar-Gorée",
                "Affiche « LMDG : nouveaux tarifs applicables à la traversée Dakar-Gorée », "
                "reprenant les montants du tableau ci-dessus.",
                "Affiche officielle des tarifs (les montants figurent aussi dans le tableau).",
            ),
            contact(),
        ],
    )


def dakar_ziguinchor():
    return (
        "La liaison maritime Dakar-Ziguinchor : horaires, tarifs, véhicules et bagages.",
        [
            image(
                "origine/baniere-dakar-zig.jpg",
                "Bannière de la liaison Dakar-Ziguinchor",
                "Bannière de la liaison maritime Dakar-Ziguinchor.",
            ),
            h("Horaires des traversées"),
            h("De Dakar à Ziguinchor", "h3"),
            table(
                ["Navire", "Départ", "Arrivée"],
                [
                    ["Aguene", "Mardi 20h", "Mercredi 11h"],
                    ["Diambogne", "Jeudi 20h", "Vendredi 11h"],
                    ["Aguene", "Vendredi 20h", "Samedi 11h"],
                    ["Diambogne", "Dimanche 20h", "Lundi 11h"],
                ],
            ),
            h("De Ziguinchor à Dakar", "h3"),
            table(
                ["Navire", "Départ", "Arrivée"],
                [
                    ["Diambogne", "Mardi 13h", "Mercredi 6h"],
                    ["Aguene", "Jeudi 13h", "Vendredi 6h"],
                    ["Diambogne", "Vendredi 13h", "Samedi 6h"],
                    ["Aguene", "Dimanche 13h", "Lundi 6h"],
                ],
            ),
            h("Tarifs"),
            table(
                ["Catégorie", "Sénégalais et résidents", "Étrangers non-résidents"],
                [
                    ["1re catégorie (2 places)", "26 500 F CFA", "30 500 F CFA"],
                    ["2e catégorie (4 places)", "24 500 F CFA", "28 500 F CFA"],
                    ["3e catégorie (8 places)", "12 500 F CFA", "18 500 F CFA"],
                    ["4e catégorie (fauteuil pullman)", "5 000 F CFA", "15 500 F CFA"],
                ],
            ),
            h("Tarifs spéciaux", "h3"),
            ul(
                [
                    "Bébés, de 0 à moins de 4 ans : gratuit ;",
                    "Enfants, de 5 à moins de 12 ans : demi-tarif.",
                ]
            ),
            h("Véhicules", "h3"),
            table(["Véhicule", "Tarif"], [["Voiture", "63 000 F CFA"], ["Moto", "30 000 F CFA"]]),
            h("Bagages"),
            p(
                "Jusqu'à 200 kg par passager. Possibilité d'enregistrer vos bagages tous les "
                "jours de 8h30 à 17h."
            ),
            contact(),
        ],
    )


def politique_surete():
    return (
        "La politique de sûreté de la Gare Maritime Internationale de Dakar (GMID).",
        [
            p(
                "La présente politique définit les orientations spécifiques en matière de sûreté "
                "de la Gare Maritime Internationale de Dakar (GMID), installation portuaire "
                "dédiée au transport de passagers et de marchandises à destination de Gorée et "
                "Ziguinchor."
            ),
            h("Contexte du secteur maritime et portuaire"),
            ul(
                [
                    "Exigences de conformité",
                    "Chocs exogènes et endogènes majeurs",
                    "Exigences d'adaptation, de performance durable et de résilience",
                ]
            ),
            h("Alignement au système de management intégré (SMI)"),
            ul(
                [
                    "Approche structurée et basée sur la politique QSSE",
                    "Approche basée sur les risques",
                    "Amélioration continue en matière de sûreté",
                ]
            ),
            h("Quatre leviers"),
            ul(
                [
                    "Levier 1 : gouvernance et compétences",
                    "Levier 2 : performance opérationnelle",
                    "Levier 3 : modernisation",
                    "Levier 4 : résilience et durabilité",
                ]
            ),
            h("Objectifs de sûreté"),
            ul(
                [
                    "Sûreté physique",
                    "Sûreté opérationnelle",
                    "Sécurité des systèmes d'information",
                    "Sûreté de la chaîne logistique",
                ]
            ),
            ul(
                [
                    "Garantir la protection des personnes, des biens et des infrastructures",
                    "Prévenir les actes illicites (intrusion, sabotage, terrorisme, fraude)",
                    "Assurer la conformité légale et réglementaire, notamment au Code ISPS et "
                    "aux exigences des normes ISO 28000 et 27001",
                    "Mettre en place une approche basée sur les risques et opportunités sûreté",
                    "Renforcer la résilience opérationnelle face aux menaces",
                    "Développer une culture de sûreté auprès de l'ensemble des parties prenantes",
                    "S'inscrire dans une dynamique d'amélioration continue",
                ]
            ),
            h("Engagement de la direction"),
            p(
                "Je m'engage personnellement à allouer les ressources humaines et matérielles "
                "nécessaires à la mise en œuvre de cette politique et à l'atteinte de ses "
                "objectifs."
            ),
            p(
                "Je compte sur l'engagement de tous pour adhérer et faire adhérer l'ensemble des "
                "parties prenantes à cette démarche de rigueur qui permettra d'atteindre un "
                "niveau de sûreté conforme aux exigences."
            ),
            h("Nos engagements", "h3"),
            ul(
                [
                    "<b>Amélioration continue</b> : maintenir et dynamiser l'amélioration "
                    "continue du système de management de la GMID ;",
                    "<b>Dialogue et échange avec les parties prenantes</b> : mettre en place des "
                    "cadres de concertation et de dialogue pour renforcer la performance "
                    "collective ;",
                    "<b>Respect des valeurs</b> : garantir le respect de nos valeurs de "
                    "professionnalisme, d'objectivité, de résilience, de transparence et de "
                    "solidarité.",
                ]
            ),
            p("Fait à Dakar le 3 juillet 2026. Le Directeur Général, Waly Diouf BODIANG."),
            image(
                "origine/pq_surete_gare_maritime_29_06.png",
                "Affiche de la politique sûreté GMID",
                "Affiche officielle « Politique sûreté — Gare Maritime Internationale de "
                "Dakar », dont le contenu est repris en texte ci-dessus.",
                "Affiche officielle (le contenu figure aussi en texte ci-dessus).",
            ),
        ],
    )


PAGES = {
    "trafic-passagers": trafic_passagers,
    "gare-maritime": gare_maritime,
    "dakar-goree": dakar_goree,
    "dakar-ziguinchor": dakar_ziguinchor,
    "politique-surete-gmid": politique_surete,
}


class Command(BaseCommand):
    help = "Renseigne Trafic passagers et ses sous-pages (contenu de l'ancien site)."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true", help="Réécrit le contenu existant.")

    def handle(self, *args, force: bool, **options):
        section = ServicePage.objects.filter(slug=SECTION_SLUG).first()
        if section is None:
            self.stdout.write("Rubrique introuvable : lancez seed_site_structure.")
            return
        for slug, builder in PAGES.items():
            page = section if slug == SECTION_SLUG else section.get_children().filter(slug=slug)
            page = page if slug == SECTION_SLUG else page.first()
            if page is None:
                self.stdout.write(f"{slug} : page introuvable.")
                continue
            page = page.specific
            if len(page.body) and not force:
                self.stdout.write(f"{page.title} : contenu déjà présent, ignoré.")
                continue
            summary, raw = builder()
            page.summary = summary
            page.body = ContentStreamBlock().to_python(raw)
            page.save_revision().publish()
            self.stdout.write(f"{page.title} : contenu enregistré ({len(raw)} blocs).")
