"""Sections de la page d'accueil (StreamField).

Chaque section est un bloc que les rédacteurs peuvent ajouter, réordonner, modifier ou supprimer
depuis l'éditeur Wagtail, sans développeur (modularité de contenu — niveau 2). Les sections
« dynamiques » (actualités, navires, marchés…) lisent leurs données via les services applicatifs
des autres apps : le rédacteur ne règle que les titres et les options d'affichage.
"""

from django.utils.translation import gettext as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from apps.core.blocks import ContentStreamBlock

ICON_CHOICES = [
    ("ship", "Navire"),
    ("user", "Personne"),
    ("check", "Validation"),
    ("doc", "Document"),
    ("lock", "Cadenas"),
    ("pin", "Localisation"),
    ("phone", "Téléphone"),
]

PAGE_HELP = (
    "Choisissez une page du site. À défaut, saisissez son chemin (ex. nos-services/marchandises)."
)


class LinkItemBlock(blocks.StructBlock):
    """Lien vers une page du site, avec icône."""

    label = blocks.CharBlock(max_length=80, label="Libellé")
    icon = blocks.ChoiceBlock(choices=ICON_CHOICES, default="doc", label="Icône")
    page = blocks.PageChooserBlock(required=False, label="Page", help_text=PAGE_HELP)
    url_path = blocks.CharBlock(
        required=False,
        max_length=200,
        label="Chemin de la page (si aucune page choisie)",
        help_text="Ex. nos-services/marchandises, ou une adresse complète (https://…).",
    )

    class Meta:
        icon = "link"
        label = "Lien"


class KeyFigureItemBlock(blocks.StructBlock):
    value = blocks.CharBlock(max_length=20, label="Valeur", help_text="Ex. : 22,5 M")
    label = blocks.CharBlock(max_length=80, label="Libellé")
    source = blocks.CharBlock(required=False, max_length=120, label="Source / année")

    class Meta:
        icon = "order"
        label = "Chiffre clé"


class AudienceItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=80, label="Titre")
    text = blocks.CharBlock(max_length=220, label="Description")

    class Meta:
        icon = "group"
        label = "Public"


class HomeSectionBlock(blocks.StructBlock):
    """Base des sections : gabarit dans cms/home/<nom>.html."""

    def get_context(self, value, parent_context=None):
        return super().get_context(value, parent_context)


class HeroSectionBlock(HomeSectionBlock):
    eyebrow = blocks.CharBlock(required=False, max_length=60, label="Sur-titre")
    title = blocks.CharBlock(
        max_length=120, label="Titre principal", help_text="Unique titre de niveau 1 de la page."
    )
    intro = blocks.CharBlock(required=False, max_length=255, label="Accroche")

    class Meta:
        icon = "image"
        label = "Bandeau vidéo d'accueil"
        template = "cms/home/hero.html"


class SponsoringSectionBlock(HomeSectionBlock):
    eyebrow = blocks.CharBlock(required=False, max_length=60, label="Sur-titre")
    title = blocks.CharBlock(max_length=120, label="Titre")
    text = blocks.TextBlock(required=False, label="Texte")

    class Meta:
        icon = "media"
        label = "Sponsoring (vidéo)"
        template = "cms/home/sponsoring.html"


class PillarItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=120, label="Titre du pilier")
    text = blocks.TextBlock(label="Texte")

    class Meta:
        icon = "list-ol"
        label = "Pilier"


class PresidentVisionSectionBlock(HomeSectionBlock):
    eyebrow = blocks.CharBlock(default="La vision du Président", max_length=80, label="Sur-titre")
    title = blocks.CharBlock(max_length=200, label="Titre")
    intro = blocks.RichTextBlock(label="Introduction", features=["bold", "italic", "link"])
    pillars = blocks.ListBlock(PillarItemBlock(), label="Piliers", max_num=6)
    quote = blocks.CharBlock(required=False, max_length=250, label="Citation")
    quote_author = blocks.CharBlock(required=False, max_length=120, label="Auteur de la citation")
    image = ImageChooserBlock(required=False, label="Photo")
    image_alt = blocks.CharBlock(
        required=False,
        max_length=200,
        label="Texte alternatif de la photo (obligatoire avec photo)",
    )

    class Meta:
        icon = "user"
        label = "Vision du Président"
        template = "cms/home/president_vision.html"


class DirectorWordSectionBlock(HomeSectionBlock):
    eyebrow = blocks.CharBlock(default="Mot du Directeur Général", max_length=80, label="Sur-titre")
    title = blocks.CharBlock(max_length=120, label="Titre")
    body = blocks.RichTextBlock(label="Texte", features=["bold", "italic", "ul", "ol", "link"])
    image = ImageChooserBlock(required=False, label="Photo")
    image_alt = blocks.CharBlock(
        required=False,
        max_length=200,
        label="Texte alternatif de la photo (obligatoire avec photo)",
    )

    class Meta:
        icon = "user"
        label = "Mot du Directeur Général"
        template = "cms/home/director_word.html"


class NewsSectionBlock(HomeSectionBlock):
    title = blocks.CharBlock(default="Actualités", max_length=80, label="Titre")
    count = blocks.IntegerBlock(default=4, min_value=1, max_value=8, label="Nombre d'articles")
    all_link_label = blocks.CharBlock(
        default="Toutes les actualités", max_length=80, label="Libellé du lien « tout voir »"
    )

    def get_context(self, value, parent_context=None):
        from apps.media.services import latest_articles

        context = super().get_context(value, parent_context)
        context["articles"] = latest_articles(value["count"], exclude=["note"])
        return context

    class Meta:
        icon = "doc-full"
        label = "Actualités (automatique)"
        template = "cms/home/news.html"


class ServiceBandSectionBlock(HomeSectionBlock):
    services_title = blocks.CharBlock(default="Offre de service", max_length=80, label="Titre")
    services = blocks.ListBlock(LinkItemBlock(), label="Services")
    show_movement = blocks.BooleanBlock(
        required=False, default=True, label="Afficher le mouvement des navires"
    )
    movement_title = blocks.CharBlock(
        default="Mouvement des navires", max_length=80, label="Titre du mouvement des navires"
    )

    def get_context(self, value, parent_context=None):
        from apps.navires.services import movement_summary

        context = super().get_context(value, parent_context)
        features = (parent_context or {}).get("FEATURES", {})
        if value["show_movement"] and features.get("home_ship_movement", True):
            context["movement"] = movement_summary()
        return context

    class Meta:
        icon = "site"
        label = "Offre de service + mouvement des navires"
        template = "cms/home/service_band.html"


class HubSectionBlock(HomeSectionBlock):
    title = blocks.CharBlock(max_length=120, label="Titre")
    text = blocks.TextBlock(label="Texte")
    image = ImageChooserBlock(required=False, label="Image")
    image_alt = blocks.CharBlock(
        required=False, max_length=200, label="Texte alternatif de l'image (obligatoire avec image)"
    )
    button_label = blocks.CharBlock(default="En savoir plus", max_length=60, label="Bouton")
    page = blocks.PageChooserBlock(required=False, label="Page du bouton", help_text=PAGE_HELP)
    url_path = blocks.CharBlock(required=False, max_length=200, label="Chemin de la page")

    class Meta:
        icon = "image"
        label = "Mise en avant avec image"
        template = "cms/home/hub.html"


class ProBandSectionBlock(HomeSectionBlock):
    title = blocks.CharBlock(default="Espace Pro", max_length=60, label="Titre")
    lead = blocks.CharBlock(default="Portail de service", max_length=100, label="Accroche")
    button_label = blocks.CharBlock(
        default="Se connecter au portail", max_length=60, label="Bouton"
    )

    class Meta:
        icon = "lock"
        label = "Bandeau Espace Pro"
        template = "cms/home/pro_band.html"


class NoticesSectionBlock(HomeSectionBlock):
    figures_title = blocks.CharBlock(
        default="Répartition du trafic", max_length=80, label="Titre du visuel"
    )
    figures_image = ImageChooserBlock(required=False, label="Visuel (infographie)")
    figures_alt = blocks.CharBlock(
        required=False, max_length=250, label="Description de l'infographie (obligatoire)"
    )
    title = blocks.CharBlock(default="Note aux usagers", max_length=80, label="Titre des notes")
    count = blocks.IntegerBlock(default=7, min_value=1, max_value=15, label="Nombre de notes")

    def get_context(self, value, parent_context=None):
        from apps.media.services import user_notices

        context = super().get_context(value, parent_context)
        context["notices"] = user_notices(value["count"])
        return context

    class Meta:
        icon = "warning"
        label = "Infographie + notes aux usagers"
        template = "cms/home/notices.html"


class BusinessSectionBlock(HomeSectionBlock):
    title = blocks.CharBlock(default="Faire des affaires au port", max_length=80, label="Titre")
    side_title = blocks.CharBlock(
        default="News des Affaires au port", max_length=80, label="Titre du bloc de droite"
    )
    side_text = blocks.CharBlock(
        default="Vous êtes prestataire ? Consultez les avis.", max_length=160, label="Texte"
    )

    def get_context(self, value, parent_context=None):
        from apps.marches.services import featured_tender

        context = super().get_context(value, parent_context)
        context["tender"] = featured_tender()
        return context

    class Meta:
        icon = "clipboard-list"
        label = "Faire des affaires (marchés)"
        template = "cms/home/business.html"


class JoinSectionBlock(HomeSectionBlock):
    title = blocks.CharBlock(default="Rejoignez le port", max_length=80, label="Titre")
    items = blocks.ListBlock(LinkItemBlock(), label="Liens")

    class Meta:
        icon = "group"
        label = "Recrutement (liens)"
        template = "cms/home/join.html"


class PartnersCertsSectionBlock(HomeSectionBlock):
    partners_title = blocks.CharBlock(default="Nos partenaires", max_length=80, label="Titre")
    certs_title = blocks.CharBlock(default="Certificats", max_length=80, label="Titre")

    def get_context(self, value, parent_context=None):
        from apps.cms.models import Partner
        from apps.qualite.services import valid_certifications

        context = super().get_context(value, parent_context)
        context["partners"] = Partner.objects.filter(is_active=True).select_related("logo")
        context["certifications"] = valid_certifications()
        return context

    class Meta:
        icon = "tag"
        label = "Partenaires + certificats (automatique)"
        template = "cms/home/partners_certs.html"


class KeyFiguresSectionBlock(HomeSectionBlock):
    title = blocks.CharBlock(default="Le port en chiffres", max_length=80, label="Titre")
    figures = blocks.ListBlock(KeyFigureItemBlock(), label="Chiffres", max_num=6)

    class Meta:
        icon = "order"
        label = "Chiffres clés"
        template = "cms/home/key_figures.html"


class ExploreSectionBlock(HomeSectionBlock):
    eyebrow = blocks.CharBlock(required=False, max_length=80, label="Sur-titre")
    title = blocks.CharBlock(
        default="Explorer le Port Autonome de Dakar", max_length=100, label="Titre"
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        context["featured_pages"] = (parent_context or {}).get("featured_pages", [])
        return context

    class Meta:
        icon = "list-ul"
        label = "Rubriques du site (automatique)"
        template = "cms/home/explore.html"


class AudiencesSectionBlock(HomeSectionBlock):
    eyebrow = blocks.CharBlock(required=False, max_length=80, label="Sur-titre")
    title = blocks.CharBlock(max_length=100, label="Titre")
    intro = blocks.CharBlock(required=False, max_length=255, label="Introduction")
    items = blocks.ListBlock(AudienceItemBlock(), label="Publics", max_num=4)

    class Meta:
        icon = "group"
        label = "Publics du port"
        template = "cms/home/audiences.html"


class HomeSectionsBlock(ContentStreamBlock):
    """Toutes les sections disponibles pour composer l'accueil, plus les blocs de contenu libres."""

    hero = HeroSectionBlock()
    sponsoring = SponsoringSectionBlock()
    president_vision = PresidentVisionSectionBlock()
    director_word = DirectorWordSectionBlock()
    news = NewsSectionBlock()
    service_band = ServiceBandSectionBlock()
    key_figures = KeyFiguresSectionBlock()
    hub = HubSectionBlock()
    pro_band = ProBandSectionBlock()
    notices = NoticesSectionBlock()
    business = BusinessSectionBlock()
    join = JoinSectionBlock()
    partners_certs = PartnersCertsSectionBlock()
    explore = ExploreSectionBlock()
    audiences = AudiencesSectionBlock()

    class Meta:
        block_counts = {"hero": {"max_num": 1}}


PRESIDENT_INTRO_HTML = (
    "<p>Sous l'impulsion de Son Excellence, le Président de la République "
    "<b>Bassirou Diomaye Faye</b>, le Sénégal engage une transformation historique de son secteur "
    "maritime et portuaire. Sa vision repose sur une ambition claire : faire du Port Autonome de "
    "Dakar (PAD) et de ses extensions le moteur incontournable de notre souveraineté économique "
    "et le hub logistique de référence en Afrique de l'Ouest.</p>"
    "<p>Cette orientation stratégique nationale se décline autour de trois grands piliers :</p>"
)

PRESIDENT_PILLARS = [
    {
        "title": "La souveraineté économique et l'émergence de l'économie bleue",
        "text": (
            "Pour le Président de la République, nos infrastructures portuaires ne doivent "
            "plus être de simples zones de transit, mais de véritables leviers de création "
            "de richesses nationales. La valorisation de nos ressources maritimes et la "
            "maîtrise totale de notre chaîne logistique constituent le socle de cette "
            "souveraineté retrouvée."
        ),
    },
    {
        "title": "Le maillage territorial et la modernisation des infrastructures",
        "text": (
            "La modernisation du secteur ne se limite pas à la capitale. La vision "
            "présidentielle impose une intégration harmonieuse entre le Port de Dakar et les "
            "ports régionaux (Kaolack, Ziguinchor, Saint-Louis). Les projets phares tels que "
            "le Môle 4 (Projet Jambaar) pour quadrupler nos cadences et le développement du "
            "Port en eau profonde de Ndayane incarnent cette volonté de positionner le "
            "Sénégal au premier rang du commerce mondial."
        ),
    },
    {
        "title": "La digitalisation, la performance et l'éco-responsabilité",
        "text": (
            "Le Port de Dakar de demain se veut intelligent, performant et durable. "
            "L'accélération de la dématérialisation des procédures administratives, la "
            "réduction des temps de passage des marchandises et le respect strict des normes "
            "environnementales sont au cœur de nos engagements pour garantir la "
            "compétitivité internationale de notre plateforme."
        ),
    },
]

DG_WORD_HTML = (
    "<p>Bienvenue sur le site de la Société Nationale du Port Autonome de Dakar (SNPAD).</p>"
    "<p>Le Port de Dakar est bien plus qu'une infrastructure : c'est un moteur de croissance, "
    "un instrument de souveraineté et un hub stratégique pour le Sénégal et la sous-région. "
    "Notre ambition est de consolider sa place de plateforme logistique et industrielle "
    "performante, compétitive et innovante.</p>"
    "<p>Mon engagement, à la tête de la SNPAD, repose sur sept priorités :</p>"
    "<ul>"
    "<li>Une gouvernance moderne, transparente et éthique</li>"
    "<li>Des infrastructures modernisées, pour lutter contre la congestion</li>"
    "<li>Une digitalisation intégrale des procédures</li>"
    "<li>Un dialogue constructif avec les acteurs portuaires et l'écoute des travailleurs</li>"
    "<li>Une optimisation des ressources, avec la prise en compte de l'hinterland</li>"
    "<li>L'accélération du Port de Ndayane</li>"
    "<li>Un fonctionnement 7j/7 et 24h/24</li>"
    "</ul>"
    "<p>Aucune transformation durable n'est possible sans l'engagement de chacun. Ensemble, "
    "construisons un port plus performant, plus sûr et plus respectueux de l'environnement, "
    "au service de la vision Sénégal 2050.</p>"
    "<p><b>Vive un Port Autonome de Dakar Bou Bess</b></p>"
)


def _link(label, icon, url_path):
    return {"label": label, "icon": icon, "page": None, "url_path": url_path}


def default_home_sections(page):
    """Composition par défaut de l'accueil (ordre validé : sponsoring puis actualités).

    Utilisée tant que les rédacteurs n'ont pas enregistré leur propre composition ; la commande
    `seed_home_sections` la copie dans la page pour la rendre modifiable dans l'éditeur.
    """
    sections = [
        (
            "hero",
            {
                "eyebrow": _("Port Autonome de Dakar"),
                "title": page.hero_title or _("Le port qui connecte Dakar au monde"),
                "intro": page.intro or _("Un port, un but, une foi."),
            },
        ),
        (
            "sponsoring",
            {
                "eyebrow": "Dakar 2026",
                "title": _("Le PAD au cœur des JOJ Dakar 2026"),
                "text": _(
                    "Le Port Autonome de Dakar accompagne cet événement international "
                    "et la jeunesse africaine."
                ),
            },
        ),
        (
            "president_vision",
            {
                "eyebrow": "Cap sur la souveraineté et l'excellence",
                "title": "La vision du Président Bassirou Diomaye Diakhar Faye",
                "intro": PRESIDENT_INTRO_HTML,
                "pillars": PRESIDENT_PILLARS,
                "quote": "Faire du secteur maritime le cœur battant d'un Sénégal souverain, "
                "juste et prospère.",
                "quote_author": "Bassirou Diomaye Faye, Président de la République",
                "image": None,
                "image_alt": "",
            },
        ),
        (
            "director_word",
            {
                "eyebrow": "Mot du Directeur Général",
                "title": "Un Port Autonome de Dakar Bou Bess",
                "body": DG_WORD_HTML,
                "image": None,
                "image_alt": "",
            },
        ),
        (
            "news",
            {"title": _("Actualités"), "count": 4, "all_link_label": _("Toutes les actualités")},
        ),
    ]
    figures = [
        {"value": b.value["value"], "label": b.value["label"], "source": b.value["source"]}
        for b in page.key_figures
    ]
    if figures:
        sections.append(("key_figures", {"title": _("Le port en chiffres"), "figures": figures}))
    sections += [
        (
            "partners_certs",
            {"partners_title": _("Nos partenaires"), "certs_title": _("Certificats")},
        ),
        (
            "explore",
            {
                "eyebrow": _("Un port au service de vos activités"),
                "title": _("Explorer le Port Autonome de Dakar"),
            },
        ),
    ]
    return sections
