from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()
        cls.user = User.objects.create(username='Anon')
        cls.authorized_user = Client()
        cls.authorized_user.force_login(cls.user)

        cls.user_not_author = User.objects.create(username='NotAuthor')
        cls.authorized_not_author_client = Client()
        cls.authorized_not_author_client.force_login(cls.user_not_author)

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def test_home_url_all(self):
        """Проверка что главная страница доступна всем"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url(self):
        """Проверка что страница группы доступна всем"""
        response = self.guest_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_url(self):
        """Проверка что страница профиля автора доступна всем"""
        response = self.guest_client.get('/profile/Anon/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_url(self):
        """Проверка что страница поста доступна всем"""
        response = self.guest_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_author(self):
        """Проверка что страница редактирования поста доступна автору"""
        response_author = self.authorized_user.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(
            response_author.status_code, HTTPStatus.OK
        )

    def test_post_edit_url_all(self):
        """Проверка что страница редактирования поста недоступна гостю"""
        response_all = self.guest_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(
            response_all.status_code, HTTPStatus.FOUND
        )

    def test_post_edit_not_author(self):
        """Проверка что страница редактирования поста недоступна
        залогиненному неавтору"""
        response_not_author = self.authorized_not_author_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(
            response_not_author.status_code, HTTPStatus.FOUND
        )

    def test_post_create_url(self):
        """Проверка что страница создания поста доступна
        залогиненному пользователю и недоступна гостю"""
        response_authorized = self.authorized_user.get('/create/')
        response_not_author = self.guest_client.get('/create/')

        self.assertEqual(response_authorized.status_code, HTTPStatus.OK)
        self.assertEqual(
            response_not_author.status_code,
            HTTPStatus.FOUND
        )

    def test_user_try_follow(self):
        """Проверка что ссылка на подписку доступна
        пользователю и недоступна гостю"""
        response_authorized = self.authorized_user.get('/follow/')
        response_not_author = self.guest_client.get('/follow/')

        self.assertEqual(response_authorized.status_code, HTTPStatus.OK)
        self.assertEqual(
            response_not_author.status_code,
            HTTPStatus.FOUND
        )

    def test_404_url_all(self):
        """Проверка что страница 404 доступна всем"""
        response = self.guest_client.get('/perpetual motion machine/')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """Проверка что страницы используют коррректные шаблоны"""
        cache.clear()
        templates_url_names = {
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/': 'posts/index.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_user.get(address)
                self.assertTemplateUsed(response, template)
