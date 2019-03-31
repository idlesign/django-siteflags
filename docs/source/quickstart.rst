Quickstart
==========

.. note::

    Do not forget to add the **siteflags** application to ``INSTALLED_APPS`` in your settings file (usually ``settings.py``)
    and apply migrations.


Let's suppose we want our users to report fake articles.

Inherit your model from ``siteflags.models.ModelWithFlag`` and you're almost done.

**myapp/models.py:**


.. code-block:: python

    from siteflags.models import ModelWithFlag

    class Article(ModelWithFlag):

        FLAG_FAKE = 10
        """Let's suppose we have several flag types.
        And this is a flag status for "fake" flag type.

        """

        FLAG_BOOKMARK = 20
        """And this is a flag status for "bookmark" flag type."""

        ...  # Some model fields here.

        # Now we may want define fake-related helper methods.

        def fake_mark_add(self, user, note):
            return self.set_flag(user, note=note, status=self.FLAG_FAKE)

        def fake_mark_remove(self, user):
            return self.remove_flag(user, status=self.FLAG_FAKE)

        def fake_mark_check(self, user):
            return self.is_flagged(user, status=self.FLAG_FAKE)

        ...  # Maybe also some helper methods for FLAG_BOOKMARK.



**myapp/views.py:**

.. code-block:: python


    from django.shortcuts import get_object_or_404
    from .models import Article


    def article_details(request, article_id):

        article = get_object_or_404(Article, pk=article_id)

        user = request.user
        # Let's suppose we have here only logged in users.

        post = request.POST

        if post.get('fake_set'):
            # Now a user reports this article as a fake.
            article.fake_mark_add(user, note=post.get('fake_message'))

        elif post.get('fake_remove'):
            # Or he removes a fake flag.
            article.fake_mark_remove(user)

        is_fake = article.fake_mark_check(user)
        # This you may want to pass into a template to show flag state.

        ...  # Maybe also some handling for FLAG_BOOKMARK.

        # That's how we get all article flags (any type/status)
        # for the current user.
        all_flags = article.get_flags(user)

        ...  # Maybe render a template here.


There are even more generic API methods:

.. code-block:: python

    from siteflags.models import ModelWithFlag

    # We can find flags of any type for various objects.
    # Let's pretend we also 'article', 'video' and 'image' objects
    # available in the current scope.
    flags = ModelWithFlag.get_flags_for_objects([article, video, image])

    # We can also find flags of any type by type.
    flags = ModelWithFlag.get_flags_for_types([Article])
    # And that's practically is the same as in 'all_flags'
    # of the above mentioned view.


.. note:: You can also customize ``Flag`` model by inheriting from ``siteflags.models.FlagBase``
  and setting ``SITEFLAGS_FLAG_MODEL`` in your ``settings.py``, for example::

    SITEFLAGS_FLAG_MODEL = 'myapp.MyFlag'

And that's how it's done.
