from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Group, Post

User = get_user_model()


class UserModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый slug',
            description='Тестовое описание',
        )
        cls.test_user = User.objects.create_user(
            username='Test_username')
        cls.post = Post.objects.create(
            text='test_text_text_text_text_text',
            author=User.objects.get(username='Test_username'),
            group=UserModelTest.group
        )
        cls.comment = Comment.objects.create(
            text='test_text_text_text',
            author=User.objects.create_user(username='T1000')
        )

    def test_models_correct_object_names_post(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        expected_object_name = self.post.text
        self.assertEqual(expected_object_name, str(self.post))

    def test_models_correct_object_names_group(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = self.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_models_correct_object_names_comment(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        expected_object_name = self.comment.text
        self.assertEqual(expected_object_name, str(self.comment))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'group': 'Группа',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = self.post
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
