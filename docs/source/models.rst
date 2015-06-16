ModelWithFlag Model
===================

**siteflags.models.ModelWithFlag** is practically all that's needed for flagging.



Methods
-------

.. py:method:: get_flags_for_types(mdl_classes, [user=None[, status=None[, allow_empty=False]]]):

    Returns a dictionary with flag objects associated with the given model classes (types).
    The dictionary is indexed by model classes.
    Each dict entry contains a list of associated flag objects.

    :param list mdl_classes: Classes objects (types) list to get flags for.
    :param User user: Optional user filter
    :param int status: Optional status filter
    :param bool allow_empty: Include results for all given types, even those without associated flags.


.. py:method:: get_flags_for_objects(objects_list, [user=None[, status=None]]):

    Returns a dictionary with flag objects associated with the given objects.
    The dictionary is indexed by objects IDs.
    Each dict entry contains a list of associated flag objects.

    :param list, QuerySet objects_list: Homogeneous objects list to get flags for.
    :param User user: Optional user filter
    :param int status: Optional status filter


.. py:method:: get_flags([user=None[, status=None]]):

    Returns flags for the object optionally filtered by user and/or status.

    :param User user: Optional user filter
    :param int status: Optional status filter


.. py:method:: set_flag(user[, note=None[, status=None]]):

    Flags the object.

    :param User user:
    :param str note: User-defined note for this flag.
    :param int status: Optional status integer (the meaning is defined by a developer).


.. py:method:: remove_flag([user=None[, status=None]]):

    Removes flag(s) from the object.

    :param User user: Optional user filter
    :param int status: Optional status filter


.. py:method:: is_flagged([user=None[, status=None]]):

    Returns boolean whether the objects is flagged by a user.

    :param User user:
    :param int status: Optional status filter



Customization
-------------

SiteFlags allows you to customize Flags model.

1. Define your own `flag` model inherited from `FlagBase`.

2. Now when `models.py` in your application has the definition of a custom flags model, you need
to instruct Django to use it for your project instead of a built-in one::

    # Somewhere in your settings.py do the following.
    # Here `myapp` is the name of your application, `MyFlag` is the names of your customized model.

    SITEFLAGS_FLAG_MODEL = 'myapp.MyFlag'


3. Run `manage.py syncdb` to install your customized models into DB.
