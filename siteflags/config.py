from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SiteflagsConfig(AppConfig):
    """Siteflags configuration."""

    name = 'siteflags'
    verbose_name = _('Site Flags')
