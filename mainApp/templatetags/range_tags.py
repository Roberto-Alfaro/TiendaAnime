from django import template

register = template.Library()


@register.filter
def times(value):
    """Dado un entero n, devuelve range(1, n+1) para iterar en templates.

    Uso: {% for i in 5|times %}
    """
    try:
        n = int(value)
    except Exception:
        return []
    return range(1, n + 1)
