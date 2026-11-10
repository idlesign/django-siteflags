from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SiteflagsConfig(AppConfig):
    """Siteflags configuration."""

    name = 'siteflags'
    verbose_name = _('Site Flags')
