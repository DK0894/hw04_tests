# from django.contrib.auth import get_user_model
# from django.test import TestCase, Client
# from http import HTTPStatus
#
#
# User = get_user_model()
#
#
# class UserURLTest(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#
#     def setUp(self):
#         # Создаем неавторизованный пользователя
#         self.guest_client = Client()
#         # Создаем авторизованного пользователя
#         self.user = User.objects.create_user(username='Test_username')
#         self.authorized_client = Client()
#         self.authorized_client.force_login(self.user)
#
#     def test_users_exists_at_desired_location(self):
#         url_path = {
#             '/signup/': HTTPStatus.OK,
#             '/logout/': HTTPStatus.OK,
#             '/login/': HTTPStatus.OK,
#             '/password_reset/': HTTPStatus.OK,
#             f'auth/reset/{<uidb64>}/<token>/':
#         }
