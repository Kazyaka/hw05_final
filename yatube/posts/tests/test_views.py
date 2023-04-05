# Исправлены только докстринги, остальное соотвествует
# принятому проекту 5 спринта

from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache


from ..models import Group, Post, User, Comment, Follow


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст поста',
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Тестовый комментарий'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_posts',
                                             kwargs={'slug': 'test-slug'}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username':
                                                  self.user.username}),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': '1'})
            ),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/follow.html': reverse('posts:follow_index'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        task_group_0 = first_object.group
        task_image_0 = first_object.image
        self.assertEqual(task_text_0, self.post.text)
        self.assertEqual(task_author_0, self.post.author)
        self.assertEqual(task_group_0, self.post.group)
        self.assertEqual(task_image_0, self.post.image)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse
                                              ('posts:group_posts',
                                               kwargs={'slug':
                                                       self.group.slug}))
        first_object = response.context['page_obj'][0]
        group_of_post = response.context['group']
        task_title = group_of_post.title
        task_slug = group_of_post.slug
        task_description = group_of_post.description
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        task_group_0 = first_object.group
        task_image_0 = first_object.image
        self.assertEqual(task_text_0, self.post.text)
        self.assertEqual(task_author_0, self.post.author)
        self.assertEqual(task_group_0, self.post.group)
        self.assertEqual(task_title, self.group.title)
        self.assertEqual(task_slug, self.group.slug)
        self.assertEqual(task_description, self.group.description)
        self.assertEqual(task_image_0, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:profile',
                                                      kwargs={'username':
                                                              self.user}))
        first_object = response.context['page_obj'][0]
        author_of_post = response.context['author']
        task_text_0 = first_object.text
        task_author_0 = first_object.author
        task_group_0 = first_object.group
        task_image_0 = first_object.image
        self.assertEqual(task_text_0, self.post.text)
        self.assertEqual(task_author_0, self.post.author)
        self.assertEqual(task_group_0, self.post.group)
        self.assertEqual(author_of_post, self.post.author)
        self.assertEqual(task_image_0, self.post.image)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        form_data = {
            'text': 'Текст комма',
        }
        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk}),
            data=form_data,
        )
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            )
        )

        first_object = response.context['comments'][0]

        self.assertEqual(first_object.text, 'Текст комма')
        self.assertEqual(first_object.author, self.comment.author)
        self.assertEqual(first_object.post, self.comment.post)

        self.assertEqual(Comment.objects.count(), 2)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_edit',
                                                      kwargs={'post_id': '1'}))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
                if value == reverse('posts:post_create'):
                    self.assertEqual(
                        response.context['is_edit'], False)
                else:
                    self.assertEqual(
                        response.context['is_edit'], True)

    def test_create_post_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_with_group_on_index_page(self):
        """Если при создании поста указать группу,
        пост появляется на главной странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj']
        self.assertIn(Post.objects.get(group=self.post.group), first_object)

    def test_post_with_group_on_group_list_page(self):
        """Если при создании поста указать группу,
        пост появляется на странице группы"""
        response = self.authorized_client.get(reverse('posts:group_posts',
                                              kwargs={'slug':
                                                      self.group.slug}))
        first_object = response.context['page_obj'][0]
        group = first_object.group.title
        self.assertEqual(group, self.group.title)

    def test_post_with_group_on_profile_page(self):
        """Если при создании поста указать группу,
        пост появляется на странице профиля"""
        response = self.authorized_client.get(reverse('posts:profile',
                                                      kwargs={'username':
                                                              self.user}))
        first_object = response.context['page_obj']
        self.assertIn(Post.objects.get(group=self.post.group), first_object)

    def test_post_not_in_wrong_group(self):
        """"Проверка что пост не ушел не в ту группу"""
        new_test_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='another_test-slug',
            description='Другое тестовое описание группы')
        new_test_url = reverse('posts:group_posts', args=[new_test_group.slug])
        response = self.authorized_client.get(new_test_url)
        self.assertNotIn(PostPagesTests.post, response.context['page_obj'])

    def test_comment_on_post(self):
        """Проверка добавления комментария"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.id]))

        self.assertContains(response, self.comment)

    def test_cache_work(self):
        """"Проверка корректности кеширования"""
        response = self.authorized_client.get(reverse('posts:index'))
        Post.objects.all().delete()
        response_after_delete_post = self.authorized_client.get(reverse
                                                                ('posts:index')
                                                                )
        self.assertEqual(response.content, response_after_delete_post.content)
        cache.clear()
        response_after_cache_clear = (self.authorized_client.get
                                      (reverse('posts:index')))
        self.assertNotEqual(response.content,
                            response_after_cache_clear.content)


FIRST_POST = 1
FINAL_POST = 16
POSTS_ON_FIRST_PAGE = 10
POSTS_ON_FINAL_PAGE = 5


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_pag = User.objects.create_user(username='auth_pag')
        cls.group_pag = Group.objects.create(
            title='Тестовая группа для пагинатора',
            slug='test-slug_pag',
            description='Тестовое описание группы для пагинатора',
        )
        cls.post = Post.objects.bulk_create([
            Post(text='Тестовый текст поста',
                 author=cls.user_pag,
                 group=cls.group_pag,
                 )
            for i in range(FIRST_POST, FINAL_POST)])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_pag)

    def test_paginator_index_page(self):
        """Тестрирование пагинатора на главной странице"""
        response_first = self.authorized_client.get(reverse('posts:index'))
        response_second = self.authorized_client.get(reverse('posts:index')
                                                     + '?page=2')
        self.assertEqual(len(response_first.context['page_obj']),
                         POSTS_ON_FIRST_PAGE)
        self.assertEqual(len(response_second.context['page_obj']),
                         POSTS_ON_FINAL_PAGE)

    def test_paginator_group_list_page(self):
        """Тестрирование пагинатора на странице группы"""
        response_first = (self.authorized_client.get
                          (reverse('posts:group_posts',
                                   kwargs={'slug': self.group_pag.slug})))
        response_second = (self.authorized_client.get
                           (reverse('posts:group_posts',
                                    kwargs={'slug':
                                            self.group_pag.slug}) + '?page=2'))
        self.assertEqual(len(response_first.context['page_obj']),
                         POSTS_ON_FIRST_PAGE)
        self.assertEqual(len(response_second.context['page_obj']),
                         POSTS_ON_FINAL_PAGE)

    def test_paginator_profile_page(self):
        """Тестрирование пагинатора на странице профиля автора"""
        response_first = (self.authorized_client.get
                          (reverse('posts:profile',
                                   kwargs={'username': self.user_pag})))
        response_second = (self.authorized_client.get
                           (reverse('posts:profile',
                                    kwargs={'username':
                                            self.user_pag}) + '?page=2'))
        self.assertEqual(len
                         (response_first.context['page_obj']),
                         POSTS_ON_FIRST_PAGE)
        self.assertEqual(len(response_second.context['page_obj']),
                         POSTS_ON_FINAL_PAGE)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='followingUser')
        cls.author_is_user = Client()
        cls.author_is_user.force_login(cls.author)
        cls.follower = User.objects.create_user(username='followerUser')
        cls.follower_is_user = Client()
        cls.follower_is_user.force_login(cls.follower)
        cls.unfollower = User.objects.create_user(username='User')
        cls.unfollower_is_user = Client()
        cls.unfollower_is_user.force_login(cls.unfollower)

        cls.post = Post.objects.create(
            author=cls.author,
            text='текст'
        )

    def test_user_can_follow(self):
        """Пользователь может подписаться на автора"""
        count = Follow.objects.count()
        following = Follow.objects.create(user_id=self.follower.id,
                                          author_id=self.author.id)
        self.assertEqual(Follow.objects.count(), count + 1)
        self.assertEqual(following.author, self.author)
        self.assertEqual(following.user, self.follower)

    def test_user_can_unfollow(self):
        """Пользователь может отписаться от автора"""
        Follow.objects.create(user_id=self.follower.id,
                              author_id=self.author.id)
        count_after_follow = Follow.objects.count()
        self.follower_is_user.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.author.username}))
        self.assertEqual(Follow.objects.count(), count_after_follow - 1)

    def test_view_for_followers(self):
        """Новая запись появляется в ленте у подписчиков"""
        Follow.objects.create(user_id=self.follower.id,
                              author_id=self.author.id)
        response = self.follower_is_user.get(
            reverse('posts:follow_index'),
            follow=True
        )
        self.assertEqual(self.post, response.context['page_obj'][0])

    def test_view_for_unfollowers(self):
        """Новая запись не появляется в ленте у неподписанных
        на автора пользователей. Состояние ленты до и после выхода поста
        должно быть одинаковым"""
        len_before = 0
        Follow.objects.create(user_id=self.follower.id,
                              author_id=self.author.id)
        response = self.unfollower_is_user.get(
            reverse('posts:follow_index'),
            follow=True
        )
        self.assertNotEqual(len_before, len(response.content))
