from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

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
    content_type = models.ForeignKey(ContentType, verbose_name=_('Content type'), related_name='%(app_label)s_%(class)s_flags')

    linked_object = generic.GenericForeignKey()

    class Meta:
        abstract = True
        verbose_name = _('Flag')
        verbose_name_plural = _('Flags')
        unique_together = ('content_type', 'object_id', 'user', 'status')

    def __str__(self):
        return '%s:%s status %s' % (self.content_type, self.object_id, self.status)


class Flag(FlagBase):
    """Built-in flag class. Default functionality."""


class ModelWithFlag(models.Model):
    """Helper base class for models with flags.

    Inherit from this model to be able to mark model instances.

    """

    flags = generic.GenericRelation(MODEL_FLAG)

    def get_flags(self, user=None, status=None):
        """Returns flags for the object optionally filtered by status.

        :param User user: Optional user filter
        :param int status: Optional status filter
        :return:
        """
        filter_kwargs = {}
        self.update_filter_dict(filter_kwargs, user, status)
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
        flag.save()
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
        self.update_filter_dict(filter_kwargs, user, status)
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
        self.update_filter_dict(filter_kwargs, user, status)
        return self.flags.filter(**filter_kwargs).count()

    @classmethod
    def update_filter_dict(cls, d, user, status):
        if user is not None:
            if not user.id:
                return None
            d['user'] = user
        if status is not None:
            d['status'] = status

    class Meta:
        abstract = True
