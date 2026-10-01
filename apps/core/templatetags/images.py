from django import template
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def icon(name, css_class=""):
    """Decorative line icon from the static sprite (static/img/icons.svg, Lucide)."""
    return format_html(
        '<svg class="icon{}" aria-hidden="true" focusable="false"><use href="{}#{}"></use></svg>',
        f" {css_class}" if css_class else "",
        static("img/icons.svg"),
        name,
    )


@register.simple_tag
def picture(image, alt, sizes="100vw", css_class="", priority=False):
    """<picture> with AVIF + WebP srcsets for a pre-generated image set.

    image: {"src": "catalog/name", "widths": (400, 800), "size": (w, h)} —
    files live at static/img/<src>-<width>.<avif|webp>; "size" is the largest
    variant and gives the width/height attributes that prevent layout shift.
    priority=True marks the LCP image: eager load + fetchpriority=high.
    """
    src, widths = image["src"], image["widths"]
    width, height = image["size"]

    def srcset(ext):
        return ", ".join(f"{static(f'img/{src}-{w}.{ext}')} {w}w" for w in widths)

    sources = format_html_join(
        "", '<source type="image/{}" srcset="{}" sizes="{}">', ((ext, srcset(ext), sizes) for ext in ("avif", "webp"))
    )
    loading = mark_safe(' fetchpriority="high"' if priority else ' loading="lazy"')
    return format_html(
        '<picture{}>{}<img src="{}" alt="{}" width="{}" height="{}" decoding="async"{}></picture>',
        format_html(' class="{}"', css_class) if css_class else "",
        sources,
        static(f"img/{src}-{widths[-1]}.webp"),
        alt,
        width,
        height,
        loading,
    )


@register.simple_tag
def image_url(image):
    """URL of the largest WebP variant of a pre-generated image set."""
    return static(f"img/{image['src']}-{image['widths'][-1]}.webp")
