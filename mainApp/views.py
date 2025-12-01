from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Producto, Categoria, Pedido, ImagenReferencia, Resena
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

            for img in request.FILES.getlist("imagenes"):
                ImagenReferencia.objects.create(pedido=pedido, imagen=img)

            messages.success(request, f"Pedido creado exitosamente. Tu código de seguimiento es: {pedido.token_seguimiento}")
            return redirect("seguimiento", token=pedido.token_seguimiento)
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