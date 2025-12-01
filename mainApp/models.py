from django.db import models
from django.utils.crypto import get_random_string
from django.core.validators import MinValueValidator, MaxValueValidator

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    precio_base = models.IntegerField()
    destacado = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

    def promedio_calificacion(self):
        reseñas = self.resenas.filter(aprobada=True)
        if not reseñas.exists():
            return 0
        total = sum(r.calificacion for r in reseñas)
        return round(total / reseñas.count(), 1)

    def cantidad_resenas(self):
        return self.resenas.filter(aprobada=True).count()

class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, related_name="imagenes", on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to="productos/")

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"

class Insumo(models.Model):
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=150)
    cantidad = models.IntegerField(default=0)
    unidad = models.CharField(max_length=50, blank=True, null=True)
    marca = models.CharField(max_length=100)
    color = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.cantidad} {self.unidad or 'unidades'})"

    class Meta:
        verbose_name_plural = "Insumos"

PLATAFORMAS = [
    ("facebook", "Facebook"),
    ("instagram", "Instagram"),
    ("whatsapp", "WhatsApp"),
    ("presencial", "Presencial"),
    ("web", "Página Web"),
    ("otro", "Otro"),
]

ESTADOS_PEDIDO = [
    ("solicitado", "Solicitado"),
    ("aprobado", "Aprobado"),
    ("proceso", "En proceso"),
    ("realizada", "Realizada"),
    ("entregada", "Entregada"),
    ("finalizada", "Finalizada"),
    ("cancelada", "Cancelada"),
]

ESTADO_PAGO = [
    ("pendiente", "Pendiente"),
    ("parcial", "Parcial"),
    ("pagado", "Pagado"),
]

class Pedido(models.Model):
    cliente = models.CharField(max_length=200)
    contacto = models.CharField(max_length=200)
    producto_referencia = models.ForeignKey(Producto, blank=True, null=True, on_delete=models.SET_NULL)
    descripcion = models.TextField(blank=True)
    plataforma = models.CharField(max_length=50, choices=PLATAFORMAS, default="web")
    fecha_solicitud = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default="solicitado")
    pago = models.CharField(max_length=20, choices=ESTADO_PAGO, default="pendiente")
    token_seguimiento = models.CharField(max_length=50, unique=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token_seguimiento:
            self.token_seguimiento = get_random_string(32)
        
        if self.estado == "finalizada" and self.pago != "pagado":
            raise ValueError("No se puede finalizar un pedido que no está completamente pagado")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente}"

    class Meta:
        ordering = ["-fecha_creacion"]

class ImagenReferencia(models.Model):
    pedido = models.ForeignKey(Pedido, related_name="imagenes", on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to="referencias/")

    def __str__(self):
        return f"Referencia pedido #{self.pedido_id}"

    class Meta:
        verbose_name_plural = "Imágenes de Referencia"

class Resena(models.Model):
    producto = models.ForeignKey(Producto, related_name="resenas", on_delete=models.CASCADE)
    nombre_cliente = models.CharField(max_length=100)
    email_cliente = models.EmailField(blank=True, null=True)
    calificacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación del 1 al 5"
    )
    comentario = models.TextField()
    aprobada = models.BooleanField(default=False, help_text="Marcar para mostrar en el sitio")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_creacion"]
        verbose_name_plural = "Reseñas"

    def __str__(self):
        return f"Reseña de {self.nombre_cliente} - {self.producto.nombre} ({self.calificacion}⭐)"