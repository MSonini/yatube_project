from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Group, Comment

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='AuthorizedUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )
        cls.comment = Comment.objects.create(
            text='Test comment text',
            post=cls.post,
            author=cls.user,
        )

    def test_post_model_object_name(self):
        """Проверка метода str модели Post."""
        post = self.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_group_model_object_name(self):
        """Проверка метода str модели Group."""
        group = self.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_comment_model_object_name(self):
        """Проверка метода str модели Comment."""
        comment = self.comment
        expected_object_name = comment.text[:30]
        self.assertEqual(expected_object_name, str(comment))
