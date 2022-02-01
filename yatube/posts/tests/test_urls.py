from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='AuthorizedUser')
        cls.user_2 = User.objects.create_user(username='AuthorizedUser_2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '': 'posts/index.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            '/nonexisting_page/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page(self):
        """Несуществующий URL-адрес возвращает 404"""
        response = self.guest_client.get('/non_existing_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_redirect_anonymous(self):
        """
        Перенаправление анонимного пользователя
        на страницу авторизации.
        """
        urls_redirects = {
            f'/posts/{self.post.id}/edit/':
            f'/auth/login/?next=/posts/{self.post.id}/edit/',
            '/create/': '/auth/login/?next=/create/'
        }
        for address, redirect in urls_redirects.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(
                    response, (redirect))

    def test_url_redirects_not_author(self):
        """
        Перенаправление пользователя, не являющегося автором поста,
        на главную страницу.
        """
        post_id = self.post.id
        address = f'/posts/{post_id}/edit/'
        response = self.authorized_client_2.get(address, follow=True)
        self.assertRedirects(response, reverse('posts:index'))

    def test_add_comment_authorized(self):
        """Комментарий может оставлять только авторизованный пользователь."""
        post_id = self.post.id
        address = f'/posts/{post_id}/comment/'
        response = self.guest_client.get(address, follow=True)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{post_id}/comment/'
        )
