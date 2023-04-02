from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Group, Post, User, Comment

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(
            username='post_author',
        )
        cls.non_post_author = User.objects.create_user(
            username='non_post_author',
        )
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.post_author,
            image=SimpleUploadedFile(
                name='another_small_default.gif',
                content=SMALL_GIF,
                content_type='image/gif'
            )
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )

    def setUp(self):
        self.guest_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.post_author)
        self.authorized_user_second = Client()
        self.authorized_user_second.force_login(self.non_post_author)

    def test_authorized_user_create_post(self):
        "Проверка создания поста авторизованным пользователем"
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
            'image': self.image
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.post_author.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.group_id, form_data['group'])
        self.assertEqual(post.image.name is not None, True)

    def test_authorized_user_edit_post(self):
        "Проверка редактирования поста авторизованным пользователем"
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.post_author,
            group=self.group,
            image=self.image
        )
        uploaded = SimpleUploadedFile(
            name='other_small.gif',
            content=SMALL_GIF,
            content_type='image/gif')
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_user.post(
            reverse(
                'posts:post_edit',
                args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        created_post = Post.objects.get(id=post.id)
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.author, post.author)
        self.assertEqual(created_post.group_id, form_data['group'])
        self.assertEqual(created_post.pub_date, post.pub_date)

    def test_nonauthorized_user_create_post(self):
        "Проверка создания поста неавторизованным пользователем"
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
        }
        response = self.guest_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse('login') + '?next=' + reverse('posts:post_create')
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_nonauthorized_user_edit_post(self):
        "Проверка редактирования поста неавторизованным пользователем"
        posts_count = Post.objects.count()
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.post_author,
            group=self.group,
        )
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }
        response = self.guest_user.post(
            reverse(
                'posts:post_edit',
                args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        created_post = Post.objects.get(id=post.id)
        redirect = reverse('login') + '?next=' + reverse('posts:post_edit',
                                                         kwargs={'post_id':
                                                                 post.id})
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(created_post.pub_date, post.pub_date)

    def test_authorized_user_not_edit_post(self):
        "Проверка невозможности редактирования чужого поста"
        "авторизованным пользователем"
        posts_count = Post.objects.count()
        post = Post.objects.create(
            text='Текст поста для редактирования',
            author=self.post_author,
            group=self.group,
        )
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
        }
        response = self.authorized_user_second.post(
            reverse(
                'posts:post_edit',
                args=[post.id]),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        redirect = reverse('posts:post_detail', kwargs={'post_id': post.id})
        self.assertRedirects(response, redirect)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        created_post = Post.objects.get(id=post.id)
        self.assertEqual(post.text, created_post.text)
        self.assertEqual(post.author, created_post.author)
        self.assertEqual(post.group, created_post.group)
        self.assertEqual(post.pub_date, created_post.pub_date)

    def test_authorized_user_create_post_without_group(self):
        "Проверка создания поста авторизованным пользователем"
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.post_author.username})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post_author)

    def test_add_comment(self):
        """Комментарий появляется в базе после добавления
            авторизованным пользователем"""
        comment = reverse(
            'posts:add_comment',
            kwargs={
                'post_id': self.post.id})
        comments_before = set(self.post.comments.all())
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_user.post(
            comment,
            data=form_data,
            follow=True
        )
        comments_after = set(response.context['comments'])
        list_diff = comments_before ^ comments_after
        self.assertEqual(len(list_diff), 1)
        new_comment = list_diff.pop()
        self.assertEqual(new_comment.text, 'Тестовый комментарий')
        self.assertEqual(new_comment.author, self.post_author)
        self.assertEqual(new_comment.post, self.post)
