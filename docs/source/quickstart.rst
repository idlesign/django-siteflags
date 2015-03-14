Quickstart
==========

.. note::

    Add the **siteflags* application to INSTALLED_APPS in your settings file (usually 'settings.py').


.. warning::

    Those, who are using South <1.0 for migrations with Django <1.7, add this into settings file:

    .. code-block:: python

        SOUTH_MIGRATION_MODULES = {
            'siteflags': 'siteflags.south_migrations',
        }



Let's suppose we want our users to report fake articles.

Inherit you model from **siteflags.models.ModelWithFlag** and you're almost done.

**myapp/models.py:**


.. code-block:: python

    from django.db import models

    from siteflags.models import ModelWithFlag

    class Article(models.Model, ModelWithFlag):

        FLAG_FAKE = 10

        ... # Some model fields here.



**myapp/views.py:**

.. code-block:: python


    from django.shortcuts import get_object_or_404
    from .models import Article


    def article_details(request, id):

        article = get_object_or_404(Article, pk=id)

        ...

        # Now a user reports this article as a fake.
        article.set_flag(request.user, note='Hi, I found this article a fake!', status=Article.FLAG_FAKE)

        ...


And that's how it's done.
