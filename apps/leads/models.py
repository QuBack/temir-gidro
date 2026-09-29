from django.db import models
from django.utils.translation import gettext_lazy as _


class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = "new", _("Новая")
        IN_PROGRESS = "in_progress", _("В работе")
        CLOSED = "closed", _("Закрыта")
        SPAM = "spam", _("Спам")

    name = models.CharField(_("имя"), max_length=100)
    phone = models.CharField(_("телефон"), max_length=32)
    email = models.EmailField(_("email"), blank=True)
    message = models.TextField(_("комментарий"), blank=True, max_length=2000)

    status = models.CharField(_("статус"), max_length=16, choices=Status, default=Status.NEW, db_index=True)
    manager_note = models.TextField(_("заметка менеджера"), blank=True)

    # Where the lead came from
    source_page = models.CharField(_("страница отправки"), max_length=500, blank=True)
    landing_page = models.CharField(_("страница входа"), max_length=500, blank=True)
    referrer = models.CharField(_("источник перехода"), max_length=500, blank=True)
    utm_source = models.CharField("utm_source", max_length=200, blank=True, db_index=True)
    utm_medium = models.CharField("utm_medium", max_length=200, blank=True)
    utm_campaign = models.CharField("utm_campaign", max_length=200, blank=True)
    utm_content = models.CharField("utm_content", max_length=200, blank=True)
    utm_term = models.CharField("utm_term", max_length=200, blank=True)
    language = models.CharField(_("язык сайта"), max_length=8, blank=True)

    ip = models.GenericIPAddressField(_("IP"), null=True, blank=True)
    user_agent = models.CharField(_("браузер"), max_length=300, blank=True)
    spam_reason = models.CharField(_("причина пометки спамом"), max_length=100, blank=True)

    created_at = models.DateTimeField(_("создана"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("изменена"), auto_now=True)

    class Meta:
        verbose_name = _("заявка")
        verbose_name_plural = _("заявки")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}, {self.phone}"
