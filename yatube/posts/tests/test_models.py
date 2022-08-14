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
        expected_group_name = group.title
        expected_post_name = post.text[:15]
        objects = {
            'expected_group_name': group,
            'expected_post_name': post
        }
        for value in objects.items():
            with self.subTest(value=value):
                self.assertEqual(
                    expected_group_name[1], str(expected_post_name[1]))
