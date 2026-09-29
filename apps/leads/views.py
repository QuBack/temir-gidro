from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView

from apps.core.company import COMPANY
from apps.core.mixins import SeoMixin

from .forms import LeadForm
from .models import Lead
from .notifications import notify_new_lead
from .utils import SOURCE_SESSION_KEY, UTM_FIELDS, get_client_ip, is_rate_limited


@require_http_methods(["GET", "POST"])
def lead_create(request):
    """Works as a plain HTML form (POST → redirect to the thank-you page) and,
    progressively enhanced, as a fetch() endpoint returning JSON."""
    if request.method == "GET":
        return _render_page(request, LeadForm.for_request(request))

    wants_json = "application/json" in request.headers.get("Accept", "")
    form = LeadForm(request.POST, auto_id="lead-%s")
    ip = get_client_ip(request)

    if is_rate_limited(ip):
        form.add_error(None, _("Слишком много заявок подряд. Позвоните нам: %(phone)s") % {"phone": COMPANY["phone"]})
        return _invalid(request, form, wants_json, status=429)
    if not form.is_valid():
        return _invalid(request, form, wants_json, status=400)

    lead = form.save(commit=False)
    source = request.session.get(SOURCE_SESSION_KEY, {})
    for field in UTM_FIELDS:
        setattr(lead, field, source.get(field, ""))
    lead.landing_page = source.get("landing_page", "")
    lead.referrer = source.get("referrer", "")
    lead.source_page = form.cleaned_data["page"] or request.headers.get("Referer", "")[:500]
    lead.language = get_language() or settings.LANGUAGE_CODE
    lead.ip = ip
    lead.user_agent = request.headers.get("User-Agent", "")[:300]

    # Suspected spam is kept (a false positive must never lose a real lead)
    # but hidden under the "spam" status and not announced.
    if reason := form.spam_reason():
        lead.status = Lead.Status.SPAM
        lead.spam_reason = reason
    lead.save()
    if not reason:
        transaction.on_commit(lambda: notify_new_lead(lead))

    if wants_json:
        return JsonResponse({"ok": True})
    return redirect("leads:success")


def _invalid(request, form, wants_json, status):
    if wants_json:
        return JsonResponse({"ok": False, "errors": form.errors.get_json_data()}, status=status)
    return _render_page(request, form, status=status)


def _render_page(request, form, status=200):
    context = {"lead_form": form, "seo_title": _("Оставить заявку | Temir-Gidro"), "noindex": True}
    return render(request, "leads/lead_page.html", context, status=status)


class LeadSuccessView(SeoMixin, TemplateView):
    template_name = "leads/lead_success.html"
    seo_title = _l("Заявка отправлена | Temir-Gidro")
    noindex = True
