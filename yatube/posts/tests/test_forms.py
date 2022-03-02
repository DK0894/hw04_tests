from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post

User = get_user_model()


class UserFormCreateTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description'
        )
        cls.user = User.objects.create_user(
            username='Test_username')
        cls.post = Post.objects.create(
            text='test_text',
            author=User.objects.get(username='Test_username'),
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            text='test_text_text_text',
            author=User.objects.create_user(username='T1000'),
            post=cls.post
        )
        # Создаем неавторизованный пользователя
        cls.guest_client = Client()
        # Создаем авторизованного пользователя
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_create_post(self):
        """При отправке валидной формы со страницы создания поста
        создаётся новая запись в базе данных.
        """
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        post_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            self.group.id: self.post.group.title,
            small_gif: self.post.image,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.user.username})
        )
        # Проверяем, увеличелось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверяем, что создалась запись в нужной группе
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group,
            ).exists()
        )

    def test_create_comment(self):
        """Проверка, что после успешной отправки комментарий
        появляется на странице поста
        """
        comment_count = Comment.objects.count()
        form_data = {
            'text': self.comment.text,
            'author': self.comment.author,
            'post': self.comment.post,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args={self.post.pk}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', args={self.post.pk})
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                post=self.post.pk
            ).exists()
        )

    def test_valid_form(self):
        """Проверка работы валидатора."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        valid_form_data = {
            'text': self.post.text,
            self.group.id: self.post.group.title,
            small_gif: self.post.image,
        }
        invalid_form_data = {
            'text': None,
            self.group.id: self.post.group.title,
        }
        valid_form = PostForm(data=valid_form_data)
        invalid_form = PostForm(data=invalid_form_data)
        self.assertTrue(valid_form.is_valid())
        self.assertFalse(invalid_form.is_valid())

    def test_edit_post(self):
        """При отправке валидной формы со страницы редактирования поста
        происходит изменение поста с id в БД.
        """
        post_1 = Post.objects.get(id=self.post.id)
        form_data = {
            'text': 'new_text_post',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(post_1.id,)), data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args={post_1.id})
        )
        self.assertEqual(Post.objects.get(id=post_1.id).text, 'new_text_post')
