from django.db import models

from siteflags.models import ModelWithFlag


class Comment(ModelWithFlag):

    title = models.CharField('title', max_length=255)


class Article(ModelWithFlag):

    title = models.CharField('title', max_length=255)
