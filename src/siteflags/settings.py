from django.conf import settings


MODEL_FLAG = getattr(settings, 'SITEFLAGS_FLAG_MODEL', 'siteflags.Flag')
"""Dotted path to a Flag custom model in form of `app.Model`."""
