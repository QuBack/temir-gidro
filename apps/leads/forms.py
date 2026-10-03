import hashlib
import re
import time

from django import forms
from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from .models import Lead

_TOKEN_SALT = "leads.form-rendered-at"
# A form token is good for a week: older pages are reloaded by people, not kept open.
_TOKEN_MAX_AGE = 7 * 24 * 3600
# Spam bots post links; a customer rarely needs more than one (a drawing on a file share).
_LINK = re.compile(r"https?://|www\.|\[url|<a\s", re.IGNORECASE)


class LeadForm(forms.ModelForm):
    consent = forms.BooleanField(
        label=_("Согласен на обработку персональных данных"),
        error_messages={"required": _("Без согласия мы не можем принять заявку.")},
    )
    # Honeypot: hidden from people with CSS, bots fill it in.
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )
    # Signed render timestamp: forms submitted faster than a human could are spam.
    token = forms.CharField(required=False, widget=forms.HiddenInput)
    page = forms.CharField(required=False, max_length=500, widget=forms.HiddenInput)

    class Meta:
        model = Lead
        fields = ["name", "phone", "email", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name", "maxlength": 100}),
            "phone": forms.TextInput(attrs={"type": "tel", "autocomplete": "tel", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "message": forms.Textarea(attrs={"rows": 4, "maxlength": 2000}),
        }

    @classmethod
    def for_request(cls, request):
        return cls(
            initial={"token": signing.dumps(int(time.time()), salt=_TOKEN_SALT), "page": request.path},
            auto_id="lead-%s",
        )

    def clean_phone(self):
        phone = re.sub(r"[^\d+]", "", self.cleaned_data["phone"])
        digits = phone.lstrip("+")
        if not digits.isdigit() or not 10 <= len(digits) <= 15:
            raise forms.ValidationError(_("Укажите номер телефона полностью, например +7 700 123-45-67."))
        return phone

    def clean_page(self):
        page = self.cleaned_data["page"]
        # Only same-site paths; "//host" would be protocol-relative.
        return page if page.startswith("/") and not page.startswith("//") else ""

    def spam_reason(self) -> str:
        """Empty string for a human submission, otherwise why it looks like spam."""
        if self.cleaned_data.get("website"):
            return "honeypot"
        token = self.cleaned_data.get("token", "")
        try:
            rendered_at = signing.loads(token, salt=_TOKEN_SALT)
        except signing.BadSignature:
            return "bad_token"
        age = time.time() - rendered_at
        if age < settings.LEAD_MIN_FILL_SECONDS:
            return "too_fast"
        if age > _TOKEN_MAX_AGE:
            return "stale_token"
        # One token, one lead: a bot that loaded the page once can't replay it. A real double
        # click lands here too — the first lead is already saved and announced.
        digest = hashlib.sha256(token.encode()).hexdigest()
        if not cache.add(f"lead-token:{digest}", 1, timeout=_TOKEN_MAX_AGE):
            return "token_reused"
        name, message = self.cleaned_data.get("name", ""), self.cleaned_data.get("message", "")
        if _LINK.search(name) or len(_LINK.findall(message)) > 1:
            return "links"
        return ""
