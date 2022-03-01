from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class UserViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        cls.test_user = User.objects.create_user(
            username='Test_username')
        cls.post = Post.objects.create(
            text='test_text',
            author=User.objects.get(username='Test_username'),
            group=UserViewTest.group
        )

    def setUp(self):
        # Создаем неавторизованный пользователя
        self.guest_client = Client()
        # Создаем авторизованного пользователя
        self.user = self.test_user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post = self.post
        templates_page_names = {
            reverse('posts:main_page'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'Test_username'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': f'{post.pk}'}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': f'{post.pk}'}):
                'posts/post_create.html',
        }
        for url, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_main_page_correct_context(self):
        """Проверка словаря context на странице main_page."""
        response = self.authorized_client.get(reverse('posts:main_page'))
        first_object = response.context['page_obj'][0]
        post_objects = {
            'Test_username': f'{first_object.author.username}',
            'test_text': f'{first_object.text}',
        }
        for test_obj, obj in post_objects.items():
            with self.subTest(obj=obj):
                self.assertEqual(test_obj, obj)

    def test_group_list_page_correct_context(self):
        """Проверка словаря context на странице group_list."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', args={self.group.slug})
        )
        post = response.context['page_obj'][0]
        group = response.context['group']
        self.assertEqual(group.title, 'test_group')
        self.assertEqual(group.description, 'test_description')
        self.assertEqual(group.slug, 'test_slug')
        self.assertEqual(post.text, 'test_text')

    def test_profile_page_correct_context(self):
        """Проверка словаря context на странице profile."""
        response = self.authorized_client.get(reverse(
            'posts:profile', args={self.post.author.username})
        )
        post = response.context['page_obj'][0]
        post_text = post.text
        post_author = post.author
        self.assertEqual(post_author.username, 'Test_username')
        self.assertEqual(post_text, 'test_text')
        self.assertIn(post, response.context.get('page_obj').object_list)

    def test_post_detail_correct_context(self):
        """Проверка отображения поста на странцие post_detail."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args={self.post.pk})
        )
        post = response.context.get('post')
        self.assertEqual(post.text, 'test_text')
        self.assertEqual(post.author.username, 'Test_username')

    def test_create_post_correct_context(self):
        """Проверка отображения поста на странцие create_post."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_correct_context(self):
        """Проверка отображения поста на странцие post_edit."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args={self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_first_page_contains_ten_records(self):
        """Проверка работы пагинатора на первой странице main_page,
        group_list, profile.
        """
        for i in range(1, 15):
            self.post = Post.objects.create(
                author=self.user,
                text=f'test_text_{str(i)}',
                pub_date=Post.pub_date,
                group=UserViewTest.group,
            )
        page_content = {
            self.client.get(reverse('posts:main_page')): settings.SHOW_POSTS,
            self.client.get(
                reverse('posts:group_list', args={self.group.slug})
            ): settings.SHOW_POSTS,
            self.client.get(
                reverse('posts:profile', args={self.post.author.username})
            ): settings.SHOW_POSTS,
        }
        for response, expected in page_content.items():
            with self.subTest(response=response):
                obj = len(response.context.get('page_obj').object_list)
                self.assertEqual(obj, expected)

    def test_second_page_contains_some_records(self):
        """Проверка работы пагинатора на второй странице main_page,
        group_list, profile.
        """
        for i in range(1, 15):
            self.post = Post.objects.create(
                author=self.user,
                text=f'test_text_{str(i)}',
                pub_date=Post.pub_date,
                group=UserViewTest.group,
            )
        page_content = {
            self.client.get(reverse('posts:main_page') + '?page=2'): 5,
            self.client.get(
                reverse('posts:group_list', args={self.group.slug}) + '?page=2'
            ): 5,
            self.client.get(
                reverse('posts:profile', args={self.post.author.username})
                + '?page=2'
            ): 5,
        }
        for response, expected in page_content.items():
            with self.subTest(response=response):
                obj = len(response.context.get('page_obj').object_list)
                self.assertEqual(obj, expected)

    def test_create_post_in_his_group(self):
        """Проверка, что при создании поста,
        этот пост появляется на странице group_list.
        """
        response_1 = self.authorized_client.get(
            reverse('posts:group_list', args={self.group.slug})
        )
        obj = response_1.context.get('page_obj').object_list
        self.assertIn(self.post, obj)

    def test_create_post_not_in_his_group(self):
        """Проверка, что при создании пост не попал в группу,
        для которой не был предназначен.
        """
        group_1 = Group.objects.create(
            title='test_group_1',
            slug='test_slug_1',
            description='test_description_!',
        )
        response_2 = self.authorized_client.get(
            reverse('posts:group_list', args={group_1.slug})
        )
        obj_2 = response_2.context.get('page_obj').object_list
        self.assertNotIn(self.post, obj_2)

    def test_post_in_main_page(self):
        """Проверка, что при создании пост попадает на страницу main_page"""
        response = self.authorized_client.get(reverse('posts:main_page'))
        self.assertIn(self.post, response.context.get('page_obj').object_list)

    def test_post_in_profile(self):
        """Проверка, что при создании пост попадает на страницу profile"""
        response = self.authorized_client.get(reverse(
            'posts:profile', args={self.post.author.username})
        )
        self.assertIn(self.post, response.context.get('page_obj').object_list)
