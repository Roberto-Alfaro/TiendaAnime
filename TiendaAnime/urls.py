"""
URL configuration for TiendaAnime project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from mainApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.catalogo, name="catalogo"),
    path("producto/<int:id>/", views.detalle_producto, name="detalle_producto"),
    path("solicitar/<int:id>/", views.solicitar_producto, name="solicitar_producto"),
    path("seguimiento/<str:token>/", views.seguimiento, name="seguimiento"),
    path("consultar-token/", views.consultar_token, name="consultar_token"),
    path("reporte/", views.reporte, name="reporte"),
    path("api/", include(("mainApp.api.urls", "mainApp.api"), namespace="api")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 