from uuid import uuid4

from django.utils import unittest
from django.db import models
from django.contrib.auth.models import User

from .models import ModelWithFlag


class Article(ModelWithFlag):

    title = models.CharField('title', max_length=255)


def create_user():
    user = User(username='user%s' % uuid4().hex)
    user.save()
    return user


def create_article():
    article = Article(title='article%s' % uuid4().hex)
    article.save()
    return article


class ModelWithFlagTest(unittest.TestCase):
    
    def setUp(self):
        self.user = create_user()

    def test_set_flag(self):

        flag = create_article().set_flag(self.user, note='anote', status=10)

        self.assertEqual(flag.user, self.user)
        self.assertEqual(flag.note, 'anote')
        self.assertEqual(flag.status, 10)
        
    def test_get_flags(self):
        article = create_article()

        for idx in range(1, 5):
            article.set_flag(self.user, status=idx)

        user2 = create_user()
        article.set_flag(user2, status=2)

        flags = article.get_flags()
        self.assertEqual(len(flags), 5)

        flags = article.get_flags(status=2)
        self.assertEqual(len(flags), 2)

    def test_is_flagged(self):
        article = create_article()
        self.assertFalse(article.is_flagged())

        article.set_flag(self.user, status=11)
        self.assertTrue(article.is_flagged())

        user2 = create_user()

        self.assertTrue(article.is_flagged(self.user))
        self.assertFalse(article.is_flagged(user2))

        self.assertFalse(article.is_flagged(self.user, status=12))
        self.assertTrue(article.is_flagged(self.user, status=11))

    def test_remove_flag(self):
        article = create_article()
        article.set_flag(self.user, status=11)
        article.set_flag(self.user, status=7)
        article.set_flag(self.user, status=13)
        user2 = create_user()
        article.set_flag(user2, status=11)
        article.set_flag(user2, status=13)
        user3 = create_user()
        article.set_flag(user3, status=11)

        flags = article.get_flags()
        self.assertEqual(len(flags), 6)

        article.remove_flag(user3)
        flags = article.get_flags()
        self.assertEqual(len(flags), 5)
        flags = article.get_flags(user3)
        self.assertEqual(len(flags), 0)

        article.remove_flag(self.user, status=13)
        flags = article.get_flags(self.user)
        self.assertEqual(len(flags), 2)

        article.remove_flag(status=11)
        flags = article.get_flags()
        self.assertEqual(len(flags), 2)

        article.remove_flag()
        flags = article.get_flags()
        self.assertEqual(len(flags), 0)
