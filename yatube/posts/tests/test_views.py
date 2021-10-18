from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group
from posts.forms import PostForm

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='AuthorizedClient')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-1',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа-2',
            slug='test-group-2',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group_1,
            text='Test text',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-страницы используют правильный  html-шаблон."""
        post_id = self.post.id
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post_id}
            ): 'posts/create_post.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group_1.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post_id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ): 'posts/profile.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:index')))
        self.assertEqual(
            response.context.get('page_obj')[0],
            PostsPagesTests.post)

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': self.group_1.slug})))
        self.assertEqual(
            response.context.get('page_obj')[0],
            PostsPagesTests.post)
        self.assertEqual(
            response.context.get('group'),
            PostsPagesTests.post.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.user.username})))
        self.assertEqual(
            response.context.get('page_obj')[0],
            self.post)
        self.assertEqual(
            response.context.get('author'),
            self.post.author)
        self.assertEqual(response.context.get('post_count'), 1)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        text = self.post.text[:30]
        response = (self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id})))
        self.assertEqual(response.context.get('title'), text)
        self.assertEqual(response.context.get('post_count'), 1)
        self.assertEqual(response.context.get('post'), self.post)

    def test_create_post_show_correct_context(self):
        """
        Шаблон create_post при создании поста сформирован
        с правильным контекстом.
        """
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_edit_post_show_correct_context(self):
        """
        Шаблон create_post при редактировании поста сформирован
        с правильным контекстом.
        """
        response = (self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id})))
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_created_post_on_different_pages(self):
        """Созданная запись появится на соответвующих страницах."""
        post = Post.objects.create(
            author=self.user,
            group=self.group_1,
            text='Test text 2',
        )
        urls_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group_1.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for page in urls_pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                current_post = response.context['page_obj'].object_list[0]
                self.assertEqual(current_post, post)

    def test_created_post_not_on_different_group_page(self):
        """Созданная запись не появляется на странице другой группы."""
        post = Post.objects.create(
            author=self.user,
            group=self.group_2,
            text='Test text 2',
        )
        url = reverse('posts:group_list', kwargs={'slug': self.group_1.slug})
        response = self.client.get(url)
        posts_on_page = response.context['page_obj'].object_list
        self.assertNotIn(post, posts_on_page)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='AuthorizedClient')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание',
        )
        batch_size = 14
        batch = list((Post(
            text=f'Test {i}',
            author=cls.user,
            group=cls.group)
            for i in range(batch_size)
        ))
        Post.objects.bulk_create(batch, batch_size)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Паджинатор показывает 10 записей на первой странице."""
        urls_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for page in urls_pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_four_records(self):
        """Паджинатор показывает 4 записи на второй странице."""
        urls_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for page in urls_pages:
            with self.subTest(page=page):
                response = self.client.get(reverse('posts:index') + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 4)
