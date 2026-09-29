from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "leads"

urlpatterns = [
    path(_("zayavka/"), views.lead_create, name="create"),
    path(_("zayavka/spasibo/"), views.LeadSuccessView.as_view(), name="success"),
]
