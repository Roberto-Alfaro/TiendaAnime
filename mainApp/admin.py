from django.contrib import admin
from .models import Producto, Categoria, ImagenProducto, Insumo, Pedido, ImagenReferencia, Resena

class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1
    fields = ("imagen",)

class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio_base", "destacado")
    search_fields = ("nombre",)
    list_filter = ("categoria", "destacado")
    inlines = [ImagenProductoInline]

class InsumoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "cantidad", "marca", "color")
    search_fields = ("nombre", "tipo")
    list_filter = ("tipo", "marca")

class ImagenReferenciaInline(admin.TabularInline):
    model = ImagenReferencia
    extra = 1
    fields = ("imagen",)

class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "plataforma", "estado", "pago", "fecha_creacion")
    list_filter = ("estado", "pago", "plataforma", "fecha_creacion")
    search_fields = ("cliente", "token_seguimiento", "contacto")
    inlines = [ImagenReferenciaInline]
    readonly_fields = ("token_seguimiento", "fecha_creacion")
    
    fieldsets = (
        ("Información del Cliente", {
            "fields": ("cliente", "contacto")
        }),
        ("Detalles del Pedido", {
            "fields": ("producto_referencia", "descripcion", "fecha_solicitud", "plataforma")
        }),
        ("Estado y Pago", {
            "fields": ("estado", "pago"),
            "classes": ("wide",)
        }),
        ("Sistema", {
            "fields": ("token_seguimiento", "fecha_creacion"),
            "classes": ("collapse",)
        }),
    )

    def save_model(self, request, obj, form, change):
        if obj.estado == "finalizada" and obj.pago != "pagado":
            self.message_user(request, "❌ No puedes finalizar un pedido que no está completamente pagado", level=40)
            return
        super().save_model(request, obj, form, change)

class ResenaAdmin(admin.ModelAdmin):
    list_display = ("nombre_cliente", "producto", "calificacion_stars", "aprobada", "fecha_creacion")
    list_filter = ("aprobada", "calificacion", "fecha_creacion")
    search_fields = ("nombre_cliente", "producto__nombre", "comentario")
    readonly_fields = ("fecha_creacion",)
    actions = ["aprobar_resenas", "desaprobar_resenas"]
    list_editable = ("aprobada",)

    def calificacion_stars(self, obj):
        """Muestra las estrellas en admin"""
        return "⭐" * obj.calificacion
    calificacion_stars.short_description = "Calificación"

    def aprobar_resenas(self, request, queryset):
        updated = queryset.update(aprobada=True)
        self.message_user(request, f"✅ {updated} reseña(s) aprobada(s)")
    aprobar_resenas.short_description = "Aprobar reseñas seleccionadas"

    def desaprobar_resenas(self, request, queryset):
        updated = queryset.update(aprobada=False)
        self.message_user(request, f"❌ {updated} reseña(s) desaprobada(s)")
    desaprobar_resenas.short_description = "Desaprobar reseñas seleccionadas"

admin.site.register(Categoria)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Insumo, InsumoAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(Resena, ResenaAdmin)