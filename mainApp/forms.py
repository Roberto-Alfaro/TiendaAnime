from django import forms
from .models import Pedido, ImagenReferencia, Resena

class FormPedido(forms.ModelForm):
    imagen_referencia = forms.ImageField(
        widget=forms.FileInput(attrs={
            
            "class": "form-control",
            "accept": "image/*"
        }),
        required=False,
        label="Imagen de referencia"
    )

    class Meta:
        model = Pedido
        fields = ["cliente", "contacto", "producto_referencia", "descripcion", "fecha_solicitud"]
        widgets = {
            "cliente": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tu nombre"}),
            "contacto": forms.TextInput(attrs={"class": "form-control", "placeholder": "Email, teléfono o usuario"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Describe lo que necesitas..."}),
            "fecha_solicitud": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "producto_referencia": forms.HiddenInput(),
        }
    
    def clean_contacto(self):
        contacto = self.cleaned_data.get("contacto")
        if not contacto:
            raise forms.ValidationError("El contacto es requerido (email, teléfono o usuario de red social)")
        return contacto

    def clean_cliente(self):
        cliente = self.cleaned_data.get("cliente")
        if not cliente or len(cliente.strip()) < 3:
            raise forms.ValidationError("Por favor ingresa un nombre válido")
        return cliente

    def save(self, commit=True):
        pedido = super().save(commit=commit)
        return pedido

class FormImagenReferencias(forms.ModelForm):
    class Meta:
        model = ImagenReferencia
        fields = ["imagen"]
        widgets = {
            "imagen": forms.FileInput(attrs={"class": "form-control"}),
        }

class FormResena(forms.ModelForm):
    """Formulario para que clientes dejen reseñas"""
    calificacion = forms.ChoiceField(
        choices=[(i, f"{i} ⭐") for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Calificación"
    )

    class Meta:
        model = Resena
        fields = ["nombre_cliente", "email_cliente", "calificacion", "comentario"]
        widgets = {
            "nombre_cliente": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tu nombre"}),
            "email_cliente": forms.EmailInput(attrs={"class": "form-control", "placeholder": "tu@email.com (opcional)"}),
            "comentario": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Cuéntanos tu experiencia..."}),
        }
        labels = {
            "nombre_cliente": "Nombre",
            "email_cliente": "Email (opcional)",
            "comentario": "Tu comentario",
        }