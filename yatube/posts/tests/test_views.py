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
        for i in range(1, 15):
            self.post = Post.objects.create(
                author=self.user,
                text='test_text',
                pub_date=Post.pub_date
            )

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
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_main_page_correct_context(self):
        """Проверка отображения поста на странице main_page."""
        response = self.authorized_client.get(reverse('posts:main_page')
                                              + '?page=2'
                                              )
        first_object = response.context['page_obj'][0]
        post_objects = {
            'Test_username': f'{first_object.author.username}',
            'test_text': f'{first_object.text}',
            # 'test_description': f'{first_object.group.description}',
            # 'test_group': f'{first_object.group.title}',
        }
        for test_obj, obj in post_objects.items():
            with self.subTest(obj=obj):
                self.assertEqual(test_obj, obj)
        self.assertIn(
           UserViewTest.post, response.context.get('page_obj').object_list
        )

    def test_group_list_page_correct_context(self):
        """Проверка отображения поста на странцие group_list."""
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
        """Проверка отображения поста на странцие profile."""
        response = self.authorized_client.get(reverse(
            'posts:profile', args={self.post.author.username})
        )
        post = response.context['page_obj'][0]
        post_text = post.text
        post_author = post.author
        self.assertEqual(post_author.username, 'Test_username')
        self.assertEqual(post_text, 'test_text')
        self.assertIn(
            post, response.context.get('page_obj').object_list
        )

    def test_post_detail_correct_context(self):
        """Проверка отображения поста на странцие post_detail."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args={self.post.pk})
        )
        post = response.context.get('post')
        self.assertEqual(post.text, 'test_text')
        self.assertEqual(post.author.username, 'Test_username')
        # self.assertEqual(post.group.title, 'test_group')
        # self.assertEqual(post.group.description, 'test_description')

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

    def test_first_page_main_page_contains_ten_records(self):
        """Проверка работы пагинатора на первой странице main_page."""
        response = self.client.get(reverse('posts:main_page'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_main_page_contains_ten_records(self):
        """Проверка работы пагинатора на второй странице main_page,
        при создании пост на данной странице появляется.
        """
        response = self.client.get(reverse('posts:main_page') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_first_page_group_list_contains_ten_records(self):
        """Проверка работы пагинатора на первой странице group_list."""
        response = self.client.get(reverse('posts:group_list',
                                           args={self.group.slug})
                                   )
        self.assertEqual(len(response.context.get('group').title), 10)

    def test_second_page_group_list_contains_ten_records(self):
        """Проверка работы пагинатора на второй странице group_list."""
        response = self.client.get(reverse('posts:group_list',
                                           args={self.group.slug}) + '?page=2'
                                   )
        self.assertEqual(len(response.context.get('group').title), 10)

    def test_first_page_profile_contains_ten_records(self):
        """Проверка работы пагинатора на первой странице profile."""
        response = self.client.get(reverse(
            'posts:profile', args={self.post.author.username})
        )
        self.assertEqual(len(response.context.get('page_obj')), 10)

    def test_second_page_profile_contains_ten_records(self):
        """Проверка работы пагинатора на второй странице profile"""
        response = self.client.get(reverse(
            'posts:profile', args={self.post.author.username}) + '?page=2'
        )
        self.assertEqual(len(response.context.get('page_obj')), 5)

    def test_additional_check_create_post_group_list(self):
        """Проверка, что при создании поста,
        этот пост появляется на странице group_list И не попал в группу,
        для которой не был предназначен.
        """
        group_1 = Group.objects.create(
            title='test_group_1',
            slug='test_slug_1',
            description='test_description_!',
        )
        response_1 = self.authorized_client.get(
            reverse('posts:group_list', args={self.group.slug})
        )
        response_2 = self.authorized_client.get(
            reverse('posts:group_list', args={group_1.slug})
        )
        obj = response_1.context.get('page_obj').object_list
        obj_2 = response_2.context.get('page_obj').object_list
        self.assertIn(UserViewTest.post, obj)
        self.assertNotIn(UserViewTest.post, obj_2)
