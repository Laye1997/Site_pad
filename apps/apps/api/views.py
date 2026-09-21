"""Vues de l'API publique. Les données viennent des services applicatifs des apps métier."""

from django.conf import settings
from django.http import Http404
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.navires.services import list_escales
from apps.qualite.services import valid_certifications


class EscaleSerializer(serializers.Serializer):
    navire = serializers.CharField()
    type_navire = serializers.CharField()
    pavillon = serializers.CharField()
    provenance = serializers.CharField()
    destination = serializers.CharField()
    quai = serializers.CharField()
    date_arrivee = serializers.DateField()
    date_depart = serializers.DateField(allow_null=True)
    statut = serializers.CharField()


class CertificationSerializer(serializers.Serializer):
    referentiel = serializers.CharField()
    perimetre = serializers.CharField()
    organisme = serializers.CharField()
    numero = serializers.CharField()
    date_emission = serializers.DateField()
    date_validite = serializers.DateField()


class _PublicAPIView(APIView):
    """Base : l'API publique peut être coupée par feature flag."""

    def initial(self, request, *args, **kwargs):
        if not settings.FEATURES["public_api"]:
            raise Http404
        super().initial(request, *args, **kwargs)


class EscaleListView(_PublicAPIView):
    def get(self, request):
        escales = list_escales(statut=request.query_params.get("statut"))
        return Response({"results": EscaleSerializer(escales, many=True).data})


class CertificationListView(_PublicAPIView):
    def get(self, request):
        return Response(
            {"results": CertificationSerializer(valid_certifications(), many=True).data}
        )
