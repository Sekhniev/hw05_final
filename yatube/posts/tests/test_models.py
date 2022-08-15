from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая запись для создания нового поста',
        )

    def test_group_str(self):
        group = PostModelTest.group
        post = PostModelTest.post
        objects = {
            str(group): group.title,
            str(post): post.text[:15]
        }
        for value, expected in objects.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)
