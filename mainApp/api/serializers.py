from rest_framework import serializers
from mainApp.models import Insumo, Pedido


class InsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumo
        fields = "__all__"


class PedidoCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = [
            "id",
            "cliente",
            "contacto",
            "producto_referencia",
            "descripcion",
            "plataforma",
            "fecha_solicitud",
            "estado",
            "pago",
            "token_seguimiento",
            "fecha_creacion",
        ]
        read_only_fields = ["token_seguimiento", "fecha_creacion", "id"]

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except ValueError as e:
            raise serializers.ValidationError({"detail": str(e)})

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except ValueError as e:
            raise serializers.ValidationError({"detail": str(e)})