"""Crée l'arborescence éditoriale principale du site PAD."""

from django.core.management.base import BaseCommand
from wagtail.models import Site

from apps.cms.models import StandardPage
from apps.media.models import MediaIndexPage
from apps.qualite.pages import PageQSE
from apps.recrutement.models import RecruitmentIndexPage
from apps.services.models import ServiceIndexPage, ServicePage


class Command(BaseCommand):
    help = "Crée les pages racines de l'arborescence PAD sans écraser l'existant."

    ROOT_PAGES = [
        ("Nous découvrir", "nous-decouvrir", StandardPage),
        ("Activités", "nos-services", ServiceIndexPage),
        ("Opportunités d'affaires", "opportunites-affaires", StandardPage),
        ("Espace média", "espace-media", MediaIndexPage),
        ("Infos pratiques", "infos-pratiques", StandardPage),
        ("Engagements", "engagements", StandardPage),
        ("Espace Pro et recrutement", "espace-pro-recrutement", RecruitmentIndexPage),
    ]

    DISCOVERY_TREE = [
        (
            "Présentation",
            "presentation",
            [
                ("Position géographique", "position-geographique"),
                ("Historique", "historique"),
                ("Infrastructures", "infrastructures"),
                (
                    "Organisation",
                    "organisation",
                    [
                        ("Statut et Mission", "statut-et-mission"),
                        ("Administration", "administration"),
                        ("Assemblée Générale", "assemblee-generale"),
                        ("Organigramme", "organigramme"),
                    ],
                ),
                ("Représentation commerciale", "representation-commerciale"),
            ],
        ),
        ("Notre démarche sécurité et sûreté", "notre-demarche-securite-et-surete"),
        ("Nos chiffres clés", "nos-chiffres-cles"),
        (
            "Visiter le port",
            "visiter-le-port",
            [
                ("Demande de visite", "demande-de-visite"),
                ("Visite virtuelle", "visite-virtuelle"),
            ],
        ),
        (
            "Nos partenaires",
            "nos-partenaires",
            [
                ("Partenaires stratégiques", "partenaires-strategiques"),
                ("Partenaires institutionnels", "partenaires-institutionnels"),
                ("Partenaires internationaux", "partenaires-internationaux"),
            ],
        ),
        ("Associations", "associations"),
    ]

    PRACTICAL_TREE = [
        ("Prévisions du trafic", "previsions-trafic"),
        ("Croisières", "croisieres"),
        ("Lignes régulières", "lignes-regulieres"),
        (
            "Formalités",
            "formalites",
            [("Douane", "douane"), ("Taxes portuaires", "taxes-portuaires")],
        ),
        ("Lexique", "lexique"),
        ("Heures de marées", "marees"),
        ("Météo", "meteo"),
        ("Horaires", "horaires"),
        ("Contacts", "contacts"),
        ("Accès", "acces"),
        ("FAQ", "faq"),
    ]

    OPPORTUNITIES_TREE = [
        ("Appels d'offres", "appels-offres"),
        ("Avis d'attribution", "avis-attribution"),
        ("Procédures et agréments", "procedures-agrements"),
        ("Plan de passation", "plan-passation"),
        ("Manifestation d'intérêt", "manifestation-interet"),
    ]

    MEDIA_TREE = [
        ("Actualités", "actualites"),
        (
            "Publications",
            "publications",
            [("Rapport", "rapport"), ("Tam Tam du Docker", "tam-tam-du-docker")],
        ),
        ("Communiqués de presse", "communiques-presse"),
        ("Photothèque", "phototheque"),
        ("Vidéothèque", "videotheque"),
    ]

    def handle(self, *args, **options):
        site = Site.objects.get(is_default_site=True)
        root = site.root_page.specific
        created = 0
        skipped = 0

        for title, slug, page_class in self.ROOT_PAGES:
            page, was_created = self._ensure_page(root, title, slug, page_class)
            if slug == "nos-services" and page.title != title:
                page.title = title
                page.save(update_fields=["title"])
                page.save_revision().publish()
            created += int(was_created)
            skipped += int(not was_created)
            if slug == "engagements":
                _, was_qse_created = self._ensure_page(
                    page,
                    "QSSE et RSE",
                    "qsse-rse",
                    PageQSE,
                )
                created += int(was_qse_created)
                skipped += int(not was_qse_created)
            if slug == "nos-services":
                service_created = self._ensure_services(page)
                created += service_created
            if slug == "nous-decouvrir":
                created += self._ensure_tree(page, self.DISCOVERY_TREE)
            if slug == "infos-pratiques":
                created += self._ensure_tree(page, self.PRACTICAL_TREE)
            if slug == "opportunites-affaires":
                created += self._ensure_tree(page, self.OPPORTUNITIES_TREE)
            if slug == "espace-media":
                created += self._ensure_tree(page, self.MEDIA_TREE)

        self.stdout.write(
            self.style.SUCCESS(f"{created} page(s) créée(s), {skipped} déjà présente(s).")
        )

    def _ensure_page(self, parent, title, slug, page_class):
        existing = parent.get_children().filter(slug=slug).first()
        if existing:
            return existing.specific, False

        page = page_class(title=title, slug=slug, show_in_menus=True)
        parent.add_child(instance=page)
        page.save_revision().publish()
        return page, True

    def _ensure_services(self, parent):
        services = [
            (
                "Accès nautique et balisage",
                "Sécurité maritime et aides à la navigation autour du Port de Dakar.",
                [
                    (
                        "paragraph",
                        "Pour renforcer la sécurité de la navigation dans les eaux sous sa "
                        "juridiction, le Sénégal a modernisé ses aides à la navigation : "
                        "bouées, phares et infrastructures de sécurité. La Subdivision des "
                        "Phares et Balises est gérée par le Port Autonome de Dakar par "
                        "convention depuis 1977.",
                    ),
                    ("heading", {"text": "Levés bathymétriques", "level": "h2"}),
                    (
                        "paragraph",
                        "Les équipements multifaisceaux et monofaisceaux permettent le sondage "
                        "des bassins du môle 2, de la rade extérieure de Dakar, du chenal "
                        "d'accès et des sites de Rufisque, Dakar-Gorée et Ziguinchor. Ces levés "
                        "contribuent à l'implantation des bouées et à la connaissance des fonds.",
                    ),
                    (
                        "paragraph",
                        "Les opérations couvrent notamment le sondage des bassins médian et Est "
                        "du môle 2 du PAD, la rade extérieure de Dakar, le chenal d'accès du "
                        "quai de Rufisque, l'embarcadère Dakar-Gorée, le fleuve Casamance de "
                        "l'embouchure au Port de Ziguinchor, la Brèche de Saint-Louis et les "
                        "chenaux "
                        "extérieur du Port.",
                    ),
                    ("heading", {"text": "Aide à la navigation", "level": "h2"}),
                    (
                        "paragraph",
                        "Le dispositif comprend des phares et feux d'atterrissage, les feux des "
                        "jetées Nord et Sud du PAD, des bouées ordinaires et des bouées lumineuses "
                        "sur la rade de Dakar, Mbour, le Saloum et la Casamance.",
                    ),
                    (
                        "paragraph",
                        "Les phares et feux desservent notamment Saint-Louis, Kayar, Fass Boye, "
                        "les Almadies, Gorée, Diockoul, Yenne, Mbour, Joal, Djogué, les Mamelles "
                        "et le Cap Manuel. Les bouées ordinaires balisent Dakar, Kayar, Mboro, "
                        "Popenguine, le Saloum et la Casamance; les bouées lumineuses couvrent la "
                        "rade de Dakar, Mbour, les atterrissages du Saloum et de la Casamance et "
                        "Lagoba.",
                    ),
                    ("heading", {"text": "Approche de Dakar", "level": "h2"}),
                    (
                        "paragraph",
                        "À l'approche de Dakar, les navigateurs sont guidés par les phares des "
                        "Mamelles, du Cap Manuel et des Almadies, ainsi que par un système de "
                        "bouées délimitant les obstacles, le chenal d'accès au port et les "
                        "postes d'ancrage.",
                    ),
                    (
                        "paragraph",
                        "Les bouées délimitent les obstacles à contourner, notamment le banc de "
                        "sable de Mbour, le cimetière Résolue, la zone d'obstruction entre Gorée "
                        "et le Cap Manuel ainsi que les épaves. Elles matérialisent également le "
                        "ainsi que les épaves. Elles matérialisent également le chenal d'accès "
                        "au port et le poste d'ancrage SAR/ICS pour les hydrocarbures.",
                    ),
                ],
            ),
            (
                "Trafic passagers",
                "Des liaisons maritimes et des infrastructures adaptées aux passagers.",
                [],
            ),
            (
                "Marchandises",
                "Manutention, stockage et enlèvement des marchandises au port.",
                [],
            ),
            (
                "Entreprises agréées",
                "Les prestataires autorisés à intervenir dans l'écosystème portuaire.",
                [],
            ),
        ]
        created = 0
        grouped_services = [
            (
                "Accueil navires",
                "accueil-navires",
                "Les opérations et services nécessaires à l'accueil sécurisé des navires.",
                [
                    ("Pilotage", "pilotage"),
                    ("Remorquage", "remorquage"),
                    ("Lamanage", "lamanage"),
                    ("Avitaillement", "avitaillement"),
                    ("Réparation navale", "reparation-navale"),
                ],
            ),
            (
                "Marchandises",
                "marchandises",
                "Manutention, stockage et enlèvement des marchandises.",
                [
                    ("Manutention", "manutention"),
                    ("Stockage / entreposage", "stockage-entreposage"),
                    ("Enlèvement de marchandises", "enlevement-marchandises"),
                ],
            ),
            (
                "Trafic passagers",
                "trafic-passagers",
                "Liaisons maritimes et accueil des passagers.",
                [
                    ("Gare maritime", "gare-maritime"),
                    ("Dakar-Ziguinchor", "dakar-ziguinchor"),
                    ("Dakar-Gorée", "dakar-goree"),
                    ("Politique Sûreté GMID", "politique-surete-gmid"),
                ],
            ),
        ]
        for title, slug, summary, children in grouped_services:
            group, was_created = self._ensure_service_page(parent, title, slug, summary)
            created += int(was_created)
            for child_title, child_slug in children:
                _, child_created = self._ensure_service_page(
                    group,
                    child_title,
                    child_slug,
                    summary,
                )
                created += int(child_created)
        for title, summary, body in services:
            existing = parent.get_children().filter(slug=self._slugify(title)).first()
            if existing:
                if title == "Accès nautique et balisage":
                    service = existing.specific
                    service.summary = summary
                    service.body = body
                    service.save(update_fields=["summary", "body"])
                    service.save_revision().publish()
                continue
            service = ServicePage(
                title=title,
                slug=self._slugify(title),
                summary=summary,
                body=body,
            )
            parent.add_child(instance=service)
            service.save_revision().publish()
            created += 1
        return created

    @staticmethod
    def _ensure_service_page(parent, title, slug, summary):
        existing = parent.get_children().filter(slug=slug).first()
        if existing:
            return existing.specific, False
        page = ServicePage(title=title, slug=slug, summary=summary, show_in_menus=True)
        parent.add_child(instance=page)
        page.save_revision().publish()
        return page, True

    def _ensure_tree(self, parent, entries):
        created = 0
        for entry in entries:
            title, slug = entry[:2]
            children = entry[2] if len(entry) > 2 else []
            page, was_created = self._ensure_page(parent, title, slug, StandardPage)
            if slug == "notre-demarche-securite-et-surete":
                page.body = self._security_content()
                page.save(update_fields=["body"])
                page.save_revision().publish()
            created += int(was_created)
            if children:
                created += self._ensure_tree(page, children)
        return created

    @staticmethod
    def _security_content():
        return [
            (
                "paragraph",
                "Le Port Autonome de Dakar a été l'un des premiers ports en Afrique à "
                "appliquer les dispositions du Code ISPS (Code international pour la sûreté "
                "des navires et des installations portuaires), entré en vigueur le 1er "
                "juillet 2004.",
            ),
            ("heading", {"text": "Application du Code ISPS au Port de Dakar", "level": "h2"}),
            (
                "paragraph",
                "Le dispositif vise à protéger les navires, les installations portuaires et "
                "les flux contre les menaces de sûreté. Les déclarations de conformité sont "
                "délivrées par l'Autorité désignée, l'Agence nationale des affaires maritimes "
                "(ANAM), Autorité nationale de sûreté portuaire (ANSP), avec une durée de validité "
                "de cinq ans.",
            ),
            ("heading", {"text": "Installations portuaires conformes", "level": "h2"}),
            (
                "paragraph",
                "Le Port de Dakar compte treize installations portuaires conformes aux "
                "dispositions "
                "du Code ISPS : Môle 3 Hamassiré Ndouré, Môle 2 El Hadji Malick Sy, Môle 1 Cheikh "
                "Ahmadou Bamba, Dakarnave, Môle 4 Cheikh Bou Kounta, Môle 5 Cheikh Sadibou Aidara, "
                "Môle 8 Mouhamed Saïdou Ba, Wharf pétrolier Amadou Sakhir Mbaye et Jetée Nord, "
                "Terminal à conteneurs Cheikh Ibrahima Niass, Sea Line pétrole brut et gaz butane, "
                "Gare maritime internationale de Dakar Hyacinthe Thiandoum, Sea Line produits "
                "chimiques, "
                "et les postes 103 à 105 du Môle 10 Seydina Limamou Laye.",
            ),
            ("heading", {"text": "Types de trafic et opérateurs", "level": "h2"}),
            (
                "paragraph",
                "Ces installations couvrent les trafics conventionnels, les véhicules et "
                "marchandises rouliers, les navires en réparation, les vracs solides, les "
                "hydrocarbures, les conteneurs, les passagers, les produits chimiques et les "
                "produits halieutiques. Les exploitants et "
                "partenaires comprennent notamment DP World, Dakarnave, TVS, SEA INVEST, SENSTOCK, "
                "Vivo Energy, Oryx, SAR, ERES, COSAMA et LMDG.",
            ),
            ("heading", {"text": "Une démarche de sûreté portuaire continue", "level": "h2"}),
            (
                "paragraph",
                "La démarche du PAD repose sur la prévention, la conformité réglementaire, "
                "la coordination des acteurs et l'amélioration continue de la sûreté des "
                "navires et des installations.",
            ),
        ]

    @staticmethod
    def _slugify(title):
        return title.lower().replace("é", "e").replace("è", "e").replace("à", "a").replace(" ", "-")
