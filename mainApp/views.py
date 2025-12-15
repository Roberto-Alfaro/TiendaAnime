from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.contrib.auth.decorators import user_passes_test
from django.utils.dateparse import parse_date
import json
from .models import Producto, Categoria, Pedido, ImagenReferencia, Resena, ESTADOS_PEDIDO, PLATAFORMAS
from .forms import FormPedido, FormResena
from django.contrib import messages

def catalogo(request):
    categoria_id = request.GET.get("categoria")
    busqueda = (request.GET.get("buscar") or "").strip()

    productos = Producto.objects.all()

    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(categoria__nombre__icontains=busqueda)
        )

    categorias = Categoria.objects.all()
    destacados = Producto.objects.filter(destacado=True)[:6]

    return render(request, "catalogo.html", {
        "productos": productos,
        "categorias": categorias,
        "destacados": destacados,
        "categoria_activa": categoria_id,
        "busqueda": busqueda,
    })

def detalle_producto(request, id):
    producto = get_object_or_404(Producto, pk=id)
    resenas = producto.resenas.filter(aprobada=True)
    promedio = producto.promedio_calificacion()
    cantidad_resenas = producto.cantidad_resenas()

    if request.method == "POST":
        form = FormResena(request.POST)
        if form.is_valid():
            resena = form.save(commit=False)
            resena.producto = producto
            resena.save()
            messages.success(request, "¡Gracias por tu reseña! Será revisada antes de publicarse.")
            return redirect("detalle_producto", id=producto.id)
    else:
        form = FormResena()

    return render(request, "detalle_producto.html", {
        "producto": producto,
        "resenas": resenas,
        "promedio": promedio,
        "cantidad_resenas": cantidad_resenas,
        "form": form,
    })

def solicitar_producto(request, id):
    producto = get_object_or_404(Producto, pk=id)

    if request.method == "POST":
        form = FormPedido(request.POST, request.FILES)

        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.producto_referencia = producto
            pedido.plataforma = "web"
            pedido.save()

            # Capturar imagen única
            imagen = request.FILES.get("imagen_referencia")
            if imagen:
                ImagenReferencia.objects.create(pedido=pedido, imagen=imagen)

            messages.success(request, f"✅ Pedido creado exitosamente. Tu código de seguimiento es: {pedido.token_seguimiento}")
            return redirect("seguimiento", token=pedido.token_seguimiento)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = FormPedido(initial={"producto_referencia": producto.id})

    return render(request, "solicitud_pedido.html", {
        "form": form,
        "producto": producto
    })

def seguimiento(request, token):
    pedido = get_object_or_404(Pedido, token_seguimiento=token)
    return render(request, "seguimiento.html", {"pedido": pedido})

def consultar_token(request):
    pedido = None
    error = None

    if request.method == "POST":
        token = request.POST.get("token", "").strip()
        
        if not token:
            error = "Por favor ingresa un token de seguimiento"
        else:
            try:
                pedido = Pedido.objects.get(token_seguimiento=token)
            except Pedido.DoesNotExist:
                error = "Token de seguimiento no encontrado. Verifica que sea correcto."

    return render(request, "consultar_token.html", {
        "pedido": pedido,
        "error": error,
    })


def _es_staff(user):
    return user.is_active and user.is_staff


@user_passes_test(_es_staff)
def reporte(request):
    # Filtros
    fecha_desde = request.GET.get("fecha_desde")
    fecha_hasta = request.GET.get("fecha_hasta")
    estado_sel = request.GET.getlist("estado")

    qs = Pedido.objects.all()

    if fecha_desde:
        d = parse_date(fecha_desde)
        if d:
            qs = qs.filter(fecha_creacion__date__gte=d)

    if fecha_hasta:
        d = parse_date(fecha_hasta)
        if d:
            qs = qs.filter(fecha_creacion__date__lte=d)

    if estado_sel:
        qs = qs.filter(estado__in=estado_sel)

    # Pedidos por estado (usar labels legibles)
    estado_map = dict(ESTADOS_PEDIDO)
    pedidos_por_estado_qs = qs.values("estado").annotate(cantidad=Count("id")).order_by("estado")
    estados_labels = [estado_map.get(p["estado"], p["estado"]) for p in pedidos_por_estado_qs]
    estados_vals = [p["cantidad"] for p in pedidos_por_estado_qs]

    # Productos más solicitados
    productos_qs = qs.values("producto_referencia__nombre").annotate(cantidad=Count("id")).order_by("-cantidad")[:10]
    productos_labels = [p["producto_referencia__nombre"] or "(sin ref)" for p in productos_qs]
    productos_vals = [p["cantidad"] for p in productos_qs]

    # Pedidos por plataforma
    plataforma_map = dict(PLATAFORMAS)
    plataformas_qs = qs.values("plataforma").annotate(cantidad=Count("id")).order_by("plataforma")
    plataformas_labels = [plataforma_map.get(p["plataforma"], p["plataforma"]) for p in plataformas_qs]
    plataformas_vals = [p["cantidad"] for p in plataformas_qs]

    context = {
        "estados_labels": json.dumps(estados_labels),
        "estados_vals": json.dumps(estados_vals),
        "productos_labels": json.dumps(productos_labels),
        "productos_vals": json.dumps(productos_vals),
        "plataformas_labels": json.dumps(plataformas_labels),
        "plataformas_vals": json.dumps(plataformas_vals),
        "filtros": {
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "estado_sel": estado_sel,
        }
    }
    context["estados_choices"] = ESTADOS_PEDIDO

    return render(request, "reporte.html", context)