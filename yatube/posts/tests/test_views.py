from django import forms


from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings


from ..models import Group, Post, User


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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_post_info(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)

    def test_forms_show_correct(self):
        context = {
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id, }),
        }
        for reverse_page in context:
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                self.assertIsInstance(
                    response.context['form'].fields['text'],
                    forms.fields.CharField)
                self.assertIsInstance(
                    response.context['form'].fields['group'],
                    forms.fields.ChoiceField)
                if reverse_page == reverse('posts:post_create'):
                    self.assertEqual(
                        response.context['is_edit'], False)
                else:
                    self.assertEqual(
                        response.context['is_edit'], True)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_post_info(response.context['page_obj'][0])
        first_object = response.context['page_obj'][0]
        task_auth_0 = first_object.author
        self.assertEqual(task_auth_0, self.post.author)
        task_image_0 = first_object.image
        self.assertEqual(task_image_0, self.post.image)

    def test_groups_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'], self.group)
        self.check_post_info(response.context['page_obj'][0])
        first_object = response.context['page_obj'][0]
        task_auth_0 = first_object.author
        self.assertEqual(task_auth_0, self.post.author)
        task_image_0 = first_object.image
        self.assertEqual(task_image_0, self.post.image)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}))
        self.assertEqual(response.context['author'], self.user)
        self.check_post_info(response.context['page_obj'][0])
        first_object = response.context['page_obj'][0]
        task_auth_0 = first_object.author
        self.assertEqual(task_auth_0, self.post.author)
        task_image_0 = first_object.image
        self.assertEqual(task_image_0, self.post.image)

    def test_detail_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}))
        self.check_post_info(response.context['post'])
        post = response.context['post']
        task_auth_0 = post.author
        self.assertEqual(task_auth_0, self.post.author)
        task_image_0 = post.image
        self.assertEqual(task_image_0, self.post.image)

    def test_comment_on_post(self):
        comment = reverse(
            'posts:add_comment',
            kwargs={
                'post_id': self.post.id})
        comments_before = set(self.post.comments.all())
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_client.post(
            comment,
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        post = response.context['post']
        page_comments = post.comments
        self.assertEqual(form_data['text'], page_comments.last().text)
        self.assertEqual(len(comments_before) + 1, len(page_comments.all()))


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        NUMBER_OF_TEST_POSTS = 15

        list_of_posts: Post = []

        cls.guest_client = Client()

        cls.user = User.objects.create(username='Anon')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        for _ in range(NUMBER_OF_TEST_POSTS):
            list_of_posts.append(
                Post(
                    text='Один из многих',
                    author=cls.user,
                    group=cls.group,
                )
            )

        Post.objects.bulk_create(list_of_posts)

    def test_paginator_on_three_pages(self):
        group_page = '/group/test-slug/'
        profile_page = '/profile/Anon/'
        index_page = '/'

        second_page = '?page=2'

        POSTS_NUMBER_ON_SECOND_PAGE: int = 5

        page_expected_posts = {
            group_page: settings.NUM_OF_POSTS,
            profile_page: settings.NUM_OF_POSTS,
            index_page: settings.NUM_OF_POSTS,
            group_page + second_page: POSTS_NUMBER_ON_SECOND_PAGE,
            profile_page + second_page: POSTS_NUMBER_ON_SECOND_PAGE,
            index_page + second_page: POSTS_NUMBER_ON_SECOND_PAGE
        }

        for page, expected_number_of_posts in page_expected_posts.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                total_posts_on_page = len(response.context['page_obj'])

                self.assertEqual(
                    total_posts_on_page,
                    expected_number_of_posts
                )
