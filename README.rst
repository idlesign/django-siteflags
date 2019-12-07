django-siteflags
================
https://github.com/idlesign/django-siteflags

.. image:: https://idlesign.github.io/lbc/py2-lbc.svg
   :target: https://idlesign.github.io/lbc/
   :alt: LBC Python 2

----

.. image:: https://img.shields.io/pypi/v/django-siteflags.svg
    :target: https://pypi.python.org/pypi/django-siteflags

.. image:: https://img.shields.io/pypi/l/django-siteflags.svg
    :target: https://pypi.python.org/pypi/django-siteflags

.. image:: https://img.shields.io/coveralls/idlesign/django-siteflags/master.svg
    :target: https://coveralls.io/r/idlesign/django-siteflags

.. image:: https://img.shields.io/travis/idlesign/django-siteflags/master.svg
    :target: https://travis-ci.org/idlesign/django-siteflags


Description
-----------

*Reusable application for Django allowing users to flag/bookmark site objects*

So you want a user to be able to put some flags on certain site entities.

Let's say you need a kind of bookmark powered service, or a site where content is flagged and moderated, or a simplified rating system or something similar.

Inherit you model from **siteflags.models.ModelWithFlag** and you're almost done.

Like that:

.. code-block:: python

    # myapp/models.py
    from siteflags.models import ModelWithFlag


    class Article(ModelWithFlag):

        ...  # Some model fields here.


And like so:

.. code-block:: python

    # myapp/views.py
    from django.shortcuts import get_object_or_404
    from .models import Article


    def article_details(request, article_id):

        article = get_object_or_404(Article, pk=article_id)

        user = request.user
        article.set_flag(user)
        article.is_flagged(user)
        article.remove_flag(user)
        
        ...


Quite simple. Quite generic. Read the documentation.


Documentation
-------------

http://django-siteflags.readthedocs.org/
