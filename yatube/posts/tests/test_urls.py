from django.test import TestCase, Client
from http import HTTPStatus
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='leo',
            password='Gamemaker2022!',
            email='test@mail.ru'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст из формы',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.login(
            username='leo',
            password='Gamemaker2022!'
        )

    def test_create_url_redirect(self):
        """Приватные адреса не доступны
        для неавторизованных пользователей"""
        private_pages_names = {
            reverse('posts:post_create'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id},
            )
        }
        for adress in private_pages_names:
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_redirect_anonymous_on_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get(reverse('posts:post_create'))
        url = urljoin(reverse('login'), "?next=/create/")
        self.assertRedirects(response, url)

    def test_redirect_anon_username_edit_post_url(self):
        """Проверка редиректа анонимного пользователя, при обращении
        к странице редактирования поста"""
        total_number_of_id = len(
            Post.objects.filter().values_list('id',
                                              flat=True))
        url = reverse('posts:post_edit',
                      kwargs={'post_id': total_number_of_id})
        response = self.guest_client.get(url)
        self.assertRedirects(response, '/auth/login/?next=' + url)

    def test_redirect_author_username_edit_post_url(self):
        """Проверка доступности страницы редактирования поста, при обращении
        автора"""
        self.authorized_client = Client()
        self.authorized_client.login()
        total_number_of_id = len(
            Post.objects.filter().values_list('id',
                                              flat=True))
        url = reverse('posts:post_edit',
                      kwargs={'post_id': total_number_of_id})
        response = self.authorized_user.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_not_author_username_edit_post_url(self):
        """Проверка редиректа при обращении к странице редактирования поста,
        авторизированным пользователем, не автором"""
        total_number_of_id = len(
            Post.objects.filter().values_list('id',
                                              flat=True))
        url = reverse('posts:post_edit',
                      kwargs={'post_id': total_number_of_id})
        response = self.authorized_user.get(url, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес соответствует заданному шаблону."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={
                    'slug': self.group.slug
                }
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={
                    'username': self.user.username
                }
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': self.post.id
                }
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_reset_form'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_change'
            ): 'users/password_change_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_user.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_exist_guest_user(self):
        """Доступ к страницам. Неавторизованный пользователь."""
        status_code_url = {
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:password_reset_form'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK,
        }
        for url, status_code in status_code_url.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url).status_code
                self.assertEqual(status_code, response)

    def test_urls_exist_authorized_user(self):
        """Доступ к страницам. Авторизованный пользователь."""
        status_code_url = {
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:password_reset_form'): HTTPStatus.OK,
            reverse('users:password_change'): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK,
        }
        for url, status_code in status_code_url.items():
            with self.subTest(url=url):
                response = self.authorized_user.get(url).status_code
                self.assertEqual(status_code, response)

    def test_page_404(self):
        response = self.guest_client.get('/password/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
