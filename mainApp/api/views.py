from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import MethodNotAllowed

from mainApp.models import Insumo, Pedido
from .serializers import InsumoSerializer, PedidoCreateUpdateSerializer
from django.utils.dateparse import parse_date


class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoCreateUpdateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed("GET", detail="No está permitido listar pedidos via API")

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed("DELETE", detail="No está permitido eliminar pedidos via API")


class PedidoFiltrarAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        fecha_desde = request.data.get("fecha_desde")
        fecha_hasta = request.data.get("fecha_hasta")
        estados = request.data.get("estados") or []
        max_results = request.data.get("max_results")

        qs = Pedido.objects.all()

        if fecha_desde:
            d = parse_date(fecha_desde)
            if d:
                qs = qs.filter(fecha_creacion__date__gte=d)

        if fecha_hasta:
            d = parse_date(fecha_hasta)
            if d:
                qs = qs.filter(fecha_creacion__date__lte=d)

        if estados and isinstance(estados, (list, tuple)):
            qs = qs.filter(estado__in=estados)

        if max_results:
            try:
                m = int(max_results)
                qs = qs[:m]
            except Exception:
                pass

        serializer = PedidoCreateUpdateSerializer(qs, many=True)
        return Response(serializer.data)
