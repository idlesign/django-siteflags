from uuid import uuid4

import pytest

from siteflags.models import ModelWithFlag


@pytest.fixture
def create_comment():
    from siteflags.tests.testapp.models import Comment

    def create_comment_():
        comment = Comment(title='comment%s' % uuid4().hex)
        comment.save()
        return comment

    return create_comment_


@pytest.fixture
def create_article():
    from siteflags.tests.testapp.models import Article

    def create_article_():
        article = Article(title='article%s' % uuid4().hex)
        article.save()
        return article

    return create_article_


class TestModelWithFlag:
    
    def test_get_flags_for_types(self, user, user_create, create_comment, create_article):

        from siteflags.tests.testapp.models import Comment, Article

        user2 = user_create()

        article_1 = create_article()
        article_2 = create_article()
        article_1.set_flag(user)
        article_1.set_flag(user2)
        article_2.set_flag(user2, status=44)

        flags = ModelWithFlag.get_flags_for_types([Article, Comment])
        assert len(flags) == 2
        assert len(flags[Article]) == 3

        comment_1 = create_comment()
        comment_2 = create_comment()
        comment_1.set_flag(user2)
        comment_1.set_flag(user)
        comment_2.set_flag(user, status=44)

        flags = ModelWithFlag.get_flags_for_types([Article, Comment])
        assert len(flags) == 2
        assert len(flags[Article]) == 3
        assert len(flags[Comment]) == 3

    def test_get_flags_for_objects(self, user, user_create, create_article):
        user2 = user_create()

        article_1 = create_article()
        article_2 = create_article()
        article_3 = create_article()
        articles_list = (article_1, article_2, article_3)

        article_1.set_flag(user)
        article_1.set_flag(user2)
        article_2.set_flag(user2, status=33)

        flags = ModelWithFlag.get_flags_for_objects(articles_list)
        assert len(flags) == len(articles_list)
        assert len(flags[article_1.pk]) == 2
        assert len(flags[article_2.pk]) == 1
        assert len(flags[article_3.pk]) == 0

        flags = ModelWithFlag.get_flags_for_objects(articles_list, user=user)
        assert len(flags) == len(articles_list)
        assert len(flags[article_1.pk]) == 1
        assert len(flags[article_2.pk]) == 0
        assert len(flags[article_3.pk]) == 0

        flags = ModelWithFlag.get_flags_for_objects(articles_list, status=33)
        assert len(flags) == len(articles_list)
        assert len(flags[article_1.pk]) == 0
        assert len(flags[article_2.pk]) == 1
        assert len(flags[article_3.pk]) == 0

    def test_set_flag(self, user, create_article):

        flag = create_article().set_flag(user, note='anote', status=10)

        assert flag.user == user
        assert flag.note == 'anote'
        assert flag.status == 10
        
    def test_get_flags(self, user, user_create, create_article):
        article = create_article()

        for idx in range(1, 5):
            article.set_flag(user, status=idx)

        user2 = user_create()
        article.set_flag(user2, status=2)

        flags = article.get_flags()
        assert len(flags) == 5

        flags = article.get_flags(status=2)
        assert len(flags) == 2

    def test_is_flagged(self, user, user_create, create_article):
        article = create_article()
        assert not article.is_flagged()

        article.set_flag(user, status=11)
        assert article.is_flagged()

        user2 = user_create()

        assert article.is_flagged(user)
        assert not article.is_flagged(user2)

        assert not article.is_flagged(user, status=12)
        assert article.is_flagged(user, status=11)

    def test_remove_flag(self, user, user_create, create_article):
        article = create_article()
        article.set_flag(user, status=11)
        article.set_flag(user, status=7)
        article.set_flag(user, status=13)
        user2 = user_create()
        article.set_flag(user2, status=11)
        article.set_flag(user2, status=13)
        user3 = user_create()
        article.set_flag(user3, status=11)

        flags = article.get_flags()
        assert len(flags) == 6

        article.remove_flag(user3)
        flags = article.get_flags()
        assert len(flags) == 5
        flags = article.get_flags(user3)
        assert len(flags) == 0

        article.remove_flag(user, status=13)
        flags = article.get_flags(user)
        assert len(flags) == 2

        article.remove_flag(status=11)
        flags = article.get_flags()
        assert len(flags) == 2

        article.remove_flag()
        flags = article.get_flags()
        assert len(flags) == 0
