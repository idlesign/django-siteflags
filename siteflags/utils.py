from etc.toolbox import get_model_class_from_settings

from siteflags import settings


def get_flag_model():
    """Returns the Flag model, set for the project."""
    return get_model_class_from_settings(settings, 'MODEL_FLAG')
