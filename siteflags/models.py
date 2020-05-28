from collections import defaultdict
from typing import List, Type, Dict, Union, Tuple, Optional, Sequence

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models, IntegrityError
from django.db.models.query import QuerySet
from django.utils.translation import gettext_lazy as _
from etc.toolbox import get_model_class_from_string

from .settings import MODEL_FLAG
from .utils import get_flag_model

if False:  # pragma: nocover
    from django.contrib.auth.models import User  # noqa

USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class FlagBase(models.Model):
    """Base class for flag models.
    Flags are marks on various site entities (model instances).

    Inherit from this model and override SITEFLAGS_FLAG_MODEL in settings.py
    to customize model fields and behaviour.

    """
    note = models.TextField(_('Note'), blank=True)
    status = models.IntegerField(_('Status'), null=True, blank=True, db_index=True)

    user = models.ForeignKey(
        USER_MODEL, related_name='%(class)s_users', verbose_name=_('User'),
        on_delete=models.CASCADE)

    time_created = models.DateTimeField(_('Date created'), auto_now_add=True)

    # Here follows a link to an object.
    object_id = models.PositiveIntegerField(verbose_name=_('Object ID'), db_index=True)

    content_type = models.ForeignKey(
        ContentType, verbose_name=_('Content type'),
        related_name='%(app_label)s_%(class)s_flags',
        on_delete=models.CASCADE)

    linked_object = GenericForeignKey()

    class Meta:

        abstract = True

        verbose_name = _('Flag')
        verbose_name_plural = _('Flags')

        unique_together = (
            'content_type',
            'object_id',
            'user',
            'status',
        )

    @classmethod
    def get_flags_for_types(
            cls,
            mdl_classes: List[Type[models.Model]],
            user: 'User' = None,
            status: int = None,
            allow_empty: bool = True

    ) -> Dict[Type[models.Model], Union[Dict[int, 'FlagBase'], Tuple]]:
        """Returns a dictionary with flag objects associated with the given model classes (types).
        The dictionary is indexed by model classes.
        Each dict entry contains a list of associated flag objects.

        :param mdl_classes:
        :param user:
        :param status:
        :param allow_empty: Flag. Include results for all given types, even those without associated flags.

        """
        if not mdl_classes or (user and not user.id):
            return {}

        types_for_models = ContentType.objects.get_for_models(*mdl_classes, for_concrete_models=False)
        filter_kwargs = {'content_type__in': types_for_models.values()}
        update_filter_dict(filter_kwargs, user, status)

        flags = cls.objects.filter(**filter_kwargs).order_by('-time_created')
        flags_dict = defaultdict(list)

        for flag in flags:
            flags_dict[flag.content_type_id].append(flag)

        result = {}  # Respect initial order.

        for mdl_cls in mdl_classes:

            content_type_id = types_for_models[mdl_cls].id

            if content_type_id in flags_dict:
                result[mdl_cls] = flags_dict[content_type_id]

            elif allow_empty:
                result[mdl_cls] = tuple()

        return result

    @classmethod
    def get_flags_for_objects(
            cls,
            objects_list: Union[QuerySet, Sequence],
            user: 'User' = None,
            status: int = None

    ) -> Dict[int, Union[Dict[int, 'FlagBase'], Tuple]]:
        """Returns a dictionary with flag objects associated with the given model objects.
        The dictionary is indexed by objects IDs.
        Each dict entry contains a list of associated flag objects.

        :param objects_list:
        :param user:
        :param status:

        """
        if not objects_list or (user and not user.id):
            return {}

        objects_ids = objects_list
        if not isinstance(objects_list, QuerySet):
            objects_ids = [obj.pk for obj in objects_list]

        filter_kwargs = {
            'object_id__in': objects_ids,
            # Consider this list homogeneous.
            'content_type': ContentType.objects.get_for_model(objects_list[0], for_concrete_model=False)
        }
        update_filter_dict(filter_kwargs, user, status)

        flags = cls.objects.filter(**filter_kwargs)
        flags_dict = defaultdict(list)

        for flag in flags:
            flags_dict[flag.object_id].append(flag)

        result = {}

        for obj in objects_list:
            if obj.pk in flags_dict:
                result[obj.pk] = flags_dict[obj.pk]

            else:
                result[obj.pk] = tuple()

        return result

    def __str__(self):
        return f'{self.content_type}:{self.object_id} status {self.status}'


class Flag(FlagBase):
    """Built-in flag class. Default functionality."""


class ModelWithFlag(models.Model):
    """Helper base class for models with flags.

    Inherit from this model to be able to mark model instances.

    """
    flags = GenericRelation(MODEL_FLAG)

    class Meta:
        abstract = True

    @classmethod
    def get_flags_for_types(
            cls,
            mdl_classes: List[Type[models.Model]],
            user: 'User' = None,
            status: int = None,
            allow_empty: bool = True

    ) -> Dict[Type[models.Model], Union[Dict[int, 'FlagBase'], Tuple]]:
        """Returns a dictionary with flag objects associated with the given model classes (types).
        The dictionary is indexed by model classes.
        Each dict entry contains a list of associated flag objects.

        :param mdl_classes:
        :param user:
        :param status:
        :param allow_empty: Flag. Include results for all given types, even those without associated flags.

        """
        model: FlagBase = get_model_class_from_string(MODEL_FLAG)
        return model.get_flags_for_types(mdl_classes, user=user, status=status, allow_empty=allow_empty)

    @classmethod
    def get_flags_for_objects(
            cls,
            objects_list: Union[QuerySet, Sequence],
            user: 'User' = None,
            status: int = None

    ) -> Dict[int, Union[Dict[int, 'FlagBase'], Tuple]]:
        """Returns a dictionary with flag objects associated with the given model objects.
        The dictionary is indexed by objects IDs.
        Each dict entry contains a list of associated flag objects.

        :param objects_list:
        :param user:
        :param status:

        """
        model: FlagBase = get_model_class_from_string(MODEL_FLAG)
        return model.get_flags_for_objects(objects_list, user=user, status=status)

    def get_flags(self, user: 'User' = None, status: int = None) -> Union[QuerySet, Sequence[FlagBase]]:
        """Returns flags for the object optionally filtered by status.

        :param user: Optional user filter
        :param status: Optional status filter

        """
        filter_kwargs = {}
        update_filter_dict(filter_kwargs, user, status)
        return self.flags.filter(**filter_kwargs).all()

    def set_flag(self, user: 'User', note: str = None, status: int = None) -> Optional[FlagBase]:
        """Flags the object.

        :param user:
        :param note: User-defined note for this flag.
        :param status: Optional status integer (the meaning is defined by a developer).

        """
        if not user.id:
            return None

        init_kwargs = {
            'user': user,
            'linked_object': self,
        }
        if note is not None:
            init_kwargs['note'] = note

        if status is not None:
            init_kwargs['status'] = status

        flag = get_flag_model()(**init_kwargs)

        try:
            flag.save()

        except IntegrityError:  # Record already exists.
            return None

        return flag

    def remove_flag(self, user: 'User' = None, status: int = None):
        """Removes flag(s) from the object.

        :param user: Optional user filter
        :param status: Optional status filter

        """
        filter_kwargs = {
            'content_type': ContentType.objects.get_for_model(self),
            'object_id': self.id
        }
        update_filter_dict(filter_kwargs, user, status)
        get_flag_model().objects.filter(**filter_kwargs).delete()

    def is_flagged(self, user: 'User' = None, status: int = None) -> int:
        """Returns a number of times the object is flagged by a user.

        :param user: Optional user filter
        :param status: Optional status filter

        """
        filter_kwargs = {
            'content_type': ContentType.objects.get_for_model(self),
            'object_id': self.id,
        }
        update_filter_dict(filter_kwargs, user, status)
        return self.flags.filter(**filter_kwargs).count()


def update_filter_dict(d: dict, user: Optional['User'], status: Optional[int]):
    """Helper. Updates filter dict for a queryset.

    :param d:
    :param user:
    :param status:

    """
    if user is not None:

        if not user.id:
            return None

        d['user'] = user

    if status is not None:
        d['status'] = status
