django-siteflags
================
https://github.com/idlesign/django-siteflags


.. image:: https://img.shields.io/pypi/v/django-siteflags.svg
    :target: https://pypi.python.org/pypi/django-siteflags

.. image:: https://img.shields.io/pypi/dm/django-siteflags.svg
    :target: https://pypi.python.org/pypi/django-siteflags

.. image:: https://img.shields.io/pypi/l/django-siteflags.svg
    :target: https://pypi.python.org/pypi/django-siteflags

.. image:: https://img.shields.io/coveralls/idlesign/django-siteflags/master.svg
    :target: https://coveralls.io/r/idlesign/django-siteflags

.. image:: https://img.shields.io/travis/idlesign/django-siteflags/master.svg
    :target: https://travis-ci.org/idlesign/django-siteflags

.. image:: https://img.shields.io/codeclimate/github/idlesign/django-siteflags.svg
   :target: https://codeclimate.com/github/idlesign/django-siteflags


Description
-----------

*Reusable application for Django allowing users to flag/bookmark site objects*

So you want a user to be able to put some flags on certain site entities.

Let's say you need a kind of bookmark powered service, or a site where content is flagged and moderated, or a simplified rating system or something similar.

Inherit you model from **siteflags.models.ModelWithFlag** and you're almost done.

Like that:

.. code-block:: python

    # myapp/models.py
    from django.db import models
    from siteflags.models import ModelWithFlag


    class Article(models.Model, ModelWithFlag):

        ... # Some model fields here.


And like so:

.. code-block:: python

    # myapp/views.py

    from django.shortcuts import get_object_or_404
    from .models import Article


    def article_details(request, id):

        article = get_object_or_404(Article, pk=id)

        ...

        # Now a user adds this article to his bookmarks.
        article.set_flag(request.user)

        ...


Quite simple.


Documentation
-------------

http://django-siteflags.readthedocs.org/
