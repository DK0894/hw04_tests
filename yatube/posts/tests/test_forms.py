from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class UserFormCreateTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        # cls.post = Post.objects.create(
        #     author=User.objects.create_user(username='auth'),
        #     text='test_text',
        #     group=UserFormCreateTest.group,
        # )
        # cls.form = PostForm()
        cls.test_user = User.objects.create_user(
            username='Test_username')
        cls.post = Post.objects.create(
            text='test_text',
            author=User.objects.get(username='Test_username'),
            group=UserFormCreateTest.group
        )

    def setUp(self):
        # Создаем неавторизованный пользователя
        self.guest_client = Client()
        # Создаем авторизованного пользователя
        self.user = self.test_user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """При отправке валидной формы со страницы создания поста
        создаётся новая запись в базе данных.
        """
        post_count = Post.objects.count()
        valid_form_data = {
            'text': self.post.text,
            UserFormCreateTest.group.id: self.post.group.title,
        }
        invalid_form_data = {
            'text': None,
            UserFormCreateTest.group.id: self.post.group.title,
        }
        # Проверяем форму на валидность
        valid_form = PostForm(data=valid_form_data)
        invalid_form = PostForm(data=invalid_form_data)
        self.assertTrue(valid_form.is_valid())
        self.assertFalse(invalid_form.is_valid())
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=valid_form_data,
            follow=True,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.user.username})
                             )
        # Проверяем, увеличелось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)
        print(post_count)
        # Проверяем, что создалась запись в нужной группе
        self.assertTrue(
            Post.objects.filter(
                text='test_text',
                group=UserFormCreateTest.group,
            ).exists()
        )

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
