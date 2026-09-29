import re
import time

from django import forms
from django.conf import settings
from django.core import signing
from django.utils.translation import gettext_lazy as _

from .models import Lead

_TOKEN_SALT = "leads.form-rendered-at"


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
        try:
            rendered_at = signing.loads(self.cleaned_data.get("token", ""), salt=_TOKEN_SALT)
        except signing.BadSignature:
            return "bad_token"
        if time.time() - rendered_at < settings.LEAD_MIN_FILL_SECONDS:
            return "too_fast"
        return ""
