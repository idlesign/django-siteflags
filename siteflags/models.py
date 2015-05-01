from collections import defaultdict, OrderedDict

from django.db import models, IntegrityError
from django.db.models.query import QuerySet
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from etc.toolbox import get_model_class_from_string

from .settings import MODEL_FLAG
from .utils import get_flag_model


USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


@python_2_unicode_compatible
class FlagBase(models.Model):
    """Base class for flag models.
    Flags are marks on various site entities (model instances).

    Inherit from this model and override SITEFLAGS_FLAG_MODEL in settings.py
    to customize model fields and behaviour.

    """
    note = models.TextField(_('Note'), blank=True)
    status = models.IntegerField(_('Status'), null=True, blank=True, db_index=True)

    user = models.ForeignKey(USER_MODEL, related_name='%(class)s_users', verbose_name=_('User'))
    time_created = models.DateTimeField(_('Date created'), auto_now_add=True)

    # Here follows a link to an object.
    object_id = models.PositiveIntegerField(verbose_name=_('Object ID'), db_index=True)
    content_type = models.ForeignKey(
        ContentType, verbose_name=_('Content type'), related_name='%(app_label)s_%(class)s_flags')

    linked_object = generic.GenericForeignKey()

    class Meta(object):
        abstract = True
        verbose_name = _('Flag')
        verbose_name_plural = _('Flags')
        unique_together = ('content_type', 'object_id', 'user', 'status')

    @classmethod
    def get_flags_for_types(cls, mdl_classes, user=None, status=None, allow_empty=True):
        """Returns a dictionary with flag objects associated with the given model classes (types).
        The dictionary is indexed by model classes.
        Each dict entry contains a list of associated flag objects.

        :param list mdl_classes:
        :param User user:
        :param int status:
        :param bool allow_empty: Flag. Include results for all given types, even those without associated flags.
        :return:
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

        result = OrderedDict()  # Respect initial order.
        for mdl_cls in mdl_classes:
            content_type_id = types_for_models[mdl_cls].id
            if content_type_id in flags_dict:
                result[mdl_cls] = flags_dict[content_type_id]
            elif allow_empty:
                result[mdl_cls] = tuple()
        return result

    @classmethod
    def get_flags_for_objects(cls, objects_list, user=None, status=None):
        """Returns a dictionary with flag objects associated with the given model objects.
        The dictionary is indexed by objects IDs.
        Each dict entry contains a list of associated flag objects.

        :param list, QuerySet objects_list:
        :param User user:
        :param int status:
        :return:
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
        return '%s:%s status %s' % (self.content_type, self.object_id, self.status)


class Flag(FlagBase):
    """Built-in flag class. Default functionality."""


class ModelWithFlag(models.Model):
    """Helper base class for models with flags.

    Inherit from this model to be able to mark model instances.

    """

    flags = generic.GenericRelation(MODEL_FLAG)

    class Meta(object):
        abstract = True

    @classmethod
    def get_flags_for_types(cls, mdl_classes, user=None, status=None, allow_empty=True):
        """Returns a dictionary with flag objects associated with the given model classes (types).
        The dictionary is indexed by model classes.
        Each dict entry contains a list of associated flag objects.

        :param list mdl_classes:
        :param User user:
        :param int status:
        :param bool allow_empty: Flag. Include results for all given types, even those without associated flags.
        :return:
        """
        return get_model_class_from_string(MODEL_FLAG).get_flags_for_types(
            mdl_classes, user=user, status=status, allow_empty=allow_empty)

    @classmethod
    def get_flags_for_objects(cls, objects_list, user=None, status=None):
        """Returns a dictionary with flag objects associated with the given model objects.
        The dictionary is indexed by objects IDs.
        Each dict entry contains a list of associated flag objects.

        :param list, QuerySet objects_list:
        :param User user:
        :param int status:
        :return:
        """
        return get_model_class_from_string(MODEL_FLAG).get_flags_for_objects(objects_list, user=user, status=status)

    def get_flags(self, user=None, status=None):
        """Returns flags for the object optionally filtered by status.

        :param User user: Optional user filter
        :param int status: Optional status filter
        :return:
        """
        filter_kwargs = {}
        update_filter_dict(filter_kwargs, user, status)
        return self.flags.filter(**filter_kwargs).all()

    def set_flag(self, user, note=None, status=None):
        """Flags the object.

        :param User user:
        :param str note: User-defined note for this flag.
        :param int status: Optional status integer (the meaning is defined by a developer).
        :return:
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
            pass
        return flag

    def remove_flag(self, user=None, status=None):
        """Removes flag(s) from the object.

        :param User user: Optional user filter
        :param int status: Optional status filter
        :return:
        """
        filter_kwargs = {
            'content_type': ContentType.objects.get_for_model(self),
            'object_id': self.id
        }
        update_filter_dict(filter_kwargs, user, status)
        get_flag_model().objects.filter(**filter_kwargs).delete()

    def is_flagged(self, user=None, status=None):
        """Returns boolean whether the objects is flagged by a user.

        :param User user: Optional user filter
        :param int status: Optional status filter
        :return:
        """
        filter_kwargs = {
            'content_type': ContentType.objects.get_for_model(self),
            'object_id': self.id,
        }
        update_filter_dict(filter_kwargs, user, status)
        return self.flags.filter(**filter_kwargs).count()


def update_filter_dict(d, user, status):
    """Helper. Updates filter dict for a queryset.

    :param dict d:
    :param User|None user:
    :param int|None status:
    :return:
    """
    if user is not None:
        if not user.id:
            return None
        d['user'] = user
    if status is not None:
        d['status'] = status
