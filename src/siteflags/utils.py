from typing import Type

from etc.toolbox import get_model_class_from_settings

from siteflags import settings

if False:  # pragma: nocover
    from .models import Flag


def get_flag_model() -> type['Flag']:
    """Returns the Flag model, set for the project."""
    return get_model_class_from_settings(settings, 'MODEL_FLAG')
