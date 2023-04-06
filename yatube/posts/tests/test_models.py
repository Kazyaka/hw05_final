from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment

User = get_user_model()

POST_TEXT_LIMIT: int = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="""Текст поста, это такой текст, который относится к посту""",
        )

    def test_models_have_correct_object_names(self):
        """Проверка, что у модели Post корректно работает __str__."""
        models = PostModelTest.post
        self.assertEqual(models.text[:POST_TEXT_LIMIT], models.__str__())

    def test_verbose_name(self):
        """Проверка verbose_name в модели Post."""
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Группа',
        }
        for field, expected_vol in field_verboses.items():
            with self.subTest(field=field):
                verbose = self.post._meta.get_field(field).verbose_name
                self.assertEqual(
                    verbose, expected_vol,
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def test_group_model_names(self):
        """Провека, что у модели Group корректный title"""
        group = GroupModelTest.group
        self.assertEqual(group.title, group.__str__())

    def test_verbose_name(self):
        """Проверка verbose_name в модели Group."""
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Адрес группы',
            'description': 'Описание',
        }
        for field, expected_vol in field_verboses.items():
            with self.subTest(field=field):
                verbose = self.group._meta.get_field(field).verbose_name
                self.assertEqual(
                    verbose, expected_vol
                )

    def test_help_text(self):
        """Проверка help_text в модели Group."""
        field_help = {
            'description': 'введите описание группы (максимум 400 символов)'
        }
        for field, expected_vol in field_help.items():
            with self.subTest(field=field):
                help_text = self.group._meta.get_field(field).help_text
                self.assertEqual(
                    help_text, expected_vol
                )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text="Текст поста, это такой текст, который относится к посту",
        )

        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Тестовый комментарий'
        )

    def test_verbose_name(self):
        """Проверка verbose_name в модели Comment."""
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор комментария',
            'created': 'Дата и время публикации',
        }
        for field, expected_vol in field_verboses.items():
            with self.subTest(value=field):
                verbose = self.comment._meta.get_field(field).verbose_name
                self.assertEqual(
                    verbose, expected_vol,
                )

    def test_comments_have_correct_object_names(self):
        """Проверка, что у модели Comment корректно работает __str__."""
        models = CommentModelTest.post
        self.assertEqual(models.text[:POST_TEXT_LIMIT], models.__str__())
