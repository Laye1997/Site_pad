"""Données des articles plus anciens repris de portdakar.sn (voir seed_old_articles).

Les pages d'origine n'affichent pas de date : les dates sont PROVISOIRES, à confirmer.
Chaque photo est un couple (fichier, texte alternatif) ; la première est l'image principale.
"""

import datetime as dt

OLDER = [
    {
        "title": "9ème session du Symposium des Chefs d'État-Major de Marine et Commandants de "
        "Gardes-Côtes du Golfe de Guinée",
        "summary": "Le Port Autonome de Dakar est honoré de participer à la 9ème session du "
        "Symposium des Chefs d'État-Major de Marine et Commandants de Gardes-Côtes du Golfe de "
        "Guinée.",
        "category": "evenement",
        "date": dt.date(2025, 11, 18),
        "paragraphs": [
            "Le Port Autonome de Dakar est honoré de participer à la 9ème session du Symposium des "
            "Chefs d'État-Major de Marine et Commandants de Gardes-Côtes du Golfe de Guinée.",
            "Cet événement constitue « un moment clé pour renforcer la coopération régionale, "
            "échanger sur les défis maritimes et œuvrer ensemble pour la sécurité et la "
            "prospérité de cette zone stratégique. »",
        ],
        "photos": [
            (
                "588018313_839236415728051_1493805661405511020_n.jpg",
                "Photo de groupe des officiers de marine et des invités du symposium, à "
                "l'extérieur.",
            ),
            (
                "587805072_839236462394713_1475878765474635788_n.jpg",
                "Salle de conférence du 9ème Symposium, avec un orateur au pupitre.",
            ),
            (
                "587260522_839236635728029_5163603745786117426_n_0.jpg",
                "Des officiers de marine en tenue blanche marchant sur une pelouse.",
            ),
            (
                "587242676_839236492394710_4756609196958933580_n.jpg",
                "Le public du symposium, composé de militaires et de civils.",
            ),
            (
                "587954572_839236689061357_4262107269985697536_n.jpg",
                "Des participants posant sur le stand du Port Autonome de Dakar.",
            ),
            (
                "587254490_839236612394698_6208863897570267399_n.jpg",
                "Des officiers visitant le stand du Port Autonome de Dakar.",
            ),
        ],
    },
    {
        "title": "Le Port Autonome de Dakar, acteur engagé pour des ports résilients en Afrique",
        "summary": "À l'occasion du 45ᵉ Conseil annuel de l'Association de Gestion des Ports de "
        "l'Afrique de l'Ouest et du Centre (AGPAOC), le PAD a représenté les enjeux portuaires "
        "sénégalais lors des panels d'autorités portuaires et partenaires.",
        "category": "actualite",
        "date": dt.date(2025, 11, 25),
        "paragraphs": [
            "Le PAD a représenté les enjeux portuaires sénégalais lors du 45ᵉ Conseil annuel de "
            "l'AGPAOC, avec la participation de Madame Ramatoulaye Ndiaye aux discussions sur le "
            "thème « Panels d'autorités portuaires et partenaires de l'AGPAOC ».",
            "La délégation dakaroise a partagé la vision et l'expérience du PAD concernant "
            "l'adaptation aux défis climatiques, la modernisation des infrastructures, la "
            "digitalisation des processus et le renforcement de la compétitivité régionale.",
            "« Cette participation s'inscrit dans la volonté du Port Autonome de Dakar de "
            "renforcer les synergies entre les ports africains. »",
        ],
        "photos": [
            (
                "579290306_831264176525275_3295732925422751248_n_0.jpg",
                "Sept participants posant sur scène lors du 45ᵉ Conseil annuel de l'AGPAOC.",
            ),
            (
                "579201324_831264133191946_6487462496689708955_n.jpg",
                "Médaille d'un prix de la meilleure performance des terminaux à conteneurs, "
                "attribué au Port Autonome de Dakar.",
            ),
            (
                "578954280_831264146525278_6877735973384402201_n.jpg",
                "Salle du 45ᵉ Conseil annuel de l'AGPAOC, avec un intervenant à l'écran.",
            ),
        ],
    },
    {
        "title": "Performance : le Port Autonome de Dakar s'affirme comme une escale de référence "
        "en Afrique de l'Ouest",
        "summary": "Grâce à une croissance soutenue du trafic de croisière, le PAD confirme son "
        "rôle stratégique dans le développement du tourisme maritime et l'attractivité du "
        "Sénégal.",
        "category": "actualite",
        "date": dt.date(2025, 9, 5),
        "paragraphs": [
            "Grâce à une croissance soutenue du trafic de croisière, le PAD confirme son rôle "
            "stratégique dans le développement du tourisme maritime et l'attractivité du "
            "Sénégal.",
            "Cette dynamique traduit non seulement un engagement fort en faveur de l'excellence, "
            "mais aussi la qualité de service et la valorisation du savoir-faire sénégalais.",
        ],
        "list_title": "Bilan croisière 2023-2024-2025 (juin)",
        "list": [
            "2023 : 24 navires et 12 771 passagers à l'arrivée de Dakar",
            "2024 : 31 navires et 17 850 passagers à l'arrivée de Dakar",
            "2025 (juin) : 29 navires et 15 554 passagers à l'arrivée de Dakar",
        ],
        "photos": [
            (
                "568341918_17987367512902890_7567402460983087175_n.jpg",
                "Bilan croisière 2023-2024-2025 : premier volet du visuel, avec un paquebot à "
                "quai.",
            ),
            (
                "568611068_17987367515902890_8870231013118836643_n.jpg",
                "Bilan croisière : deuxième volet du visuel, chiffres de 2023.",
            ),
            (
                "569244729_17987367530902890_4321603555754268035_n.jpg",
                "Bilan croisière : troisième volet du visuel, chiffres de 2024.",
            ),
            (
                "568342909_17987367533902890_7138743974617519332_n.jpg",
                "Bilan croisière : quatrième volet du visuel, chiffres de 2025 (juin).",
            ),
        ],
    },
]
