import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Same escaping as django.utils.html.json_script: keeps "</script>" and HTML
# comments inside strings from breaking out of the <script> element.
_JSON_ESCAPES = {ord(">"): "\\u003E", ord("<"): "\\u003C", ord("&"): "\\u0026"}


@register.filter
def jsonld(data):
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).translate(_JSON_ESCAPES)
    return mark_safe(f'<script type="application/ld+json">{payload}</script>')
