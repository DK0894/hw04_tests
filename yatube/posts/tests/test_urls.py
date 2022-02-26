from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class UserURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

    def setUp(self):
        # Создаем неавторизованный пользователя
        self.guest_client = Client()
        # Создаем авторизованного пользователя
        self.user = User.objects.create_user(username='Test_username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            author=self.user,
            text='test_text',
        )

    def test_pages_exists_at_desired_location(self):
        """Страницы доступны любому пользователю.
        Если страница не существует ответ 404."""
        post = self.post
        url_path = {
            '/': HTTPStatus.OK,
            '/group/test_slug/': HTTPStatus.OK,
            '/profile/Test_username/': HTTPStatus.OK,
            f'/posts/{post.pk}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, status_page in url_path.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_page)

    def test_post_edit_exists_at_desired_location_author(self):
        """Редактирование поста доступно только автору."""
        post = self.post
        response = self.authorized_client.get(f'/posts/{post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test__post_create_exists_at_desired_location_authorized(self):
        """Создание поста доступно только авторизавынному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_not_authorized_client(self):
        """Перенаправляет анонимного пользователя со страниц создания
         и редактирования поста на страницу /login/."""
        post = self.post
        url_path = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{post.pk}/edit/':
                f'/auth/login/?next=/posts/{post.pk}/edit/',
        }
        for url, redirect in url_path.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post = self.post
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/Test_username/': 'posts/profile.html',
            f'/posts/{post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/post_create.html',
            f'/posts/{post.pk}/edit/': 'posts/post_create.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
