from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from http import HTTPStatus
import tempfile
import shutil

from ..models import Post, Group, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='leo')
        cls.group = Group.objects.create(
            title='Заголовок группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст из формы',
            group=cls.group,
        )
        cls.post_author = User.objects.create_user(
            username='post_author')
        cls.comm_author = User.objects.create_user(
            username='comm_author')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)
        self.auth_user_comm = Client()
        self.auth_user_comm.force_login(self.comm_author)

    def test_post_create(self):
        """Проверка создания нового поста, авторизированным пользователем"""
        post_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        post = Post.objects.latest('id')
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(post.text, 'Тестовый текст')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.image, 'posts/small.gif')
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': 'leo'}))

    def test_authorized_user_create_comment(self):
        """Проверка создания коментария авторизированным клиентом."""
        comments_count = Comment.objects.count()
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.post_author)
        form_data = {'text': 'Тестовый коментарий'}
        response = self.auth_user_comm.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post.id}),
            data=form_data,
            follow=True)
        comment = Comment.objects.latest('id')
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.comm_author)
        self.assertEqual(comment.post_id, post.id)
        self.assertRedirects(
            response, reverse('posts:post_detail', args={post.id}))

    def test_edit_post(self):
        """Проверка редактирования поста, авторизированным пользователем"""
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.post.text, form_data['text'])
        self.assertEqual(self.post.group, self.group)
        self.assertEqual(self.post.author, self.user)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={
                'post_id': self.post.id
            }
        )
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.user,
                group=self.group,
            ).exists()
        )
