from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .paginator import paginate
from posts.forms import CommentForm, PostForm


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    page_number = request.GET.get('page')
    page_obj = paginate(post_list, page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_number = request.GET.get('page')
    page_obj = paginate(post_list, page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group', 'author')
    page_number = request.GET.get('page')
    page_obj = paginate(posts, page_number)
    following = author.following.all()

    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm()
    author = post.author
    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'author': author,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)

    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    is_edit = True
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(request, template, {'form': form, 'is_edit': is_edit})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    follows = user.follower.all()
    posts = []
    if len(follows) != 0:
        posts_combination = follows.first().author.posts.all()
        for follow in follows[1:]:
            posts.append(follow.author.posts.all())
            posts_combination = posts_combination | follow.author.posts.all()
        posts = posts_combination.order_by('-pub_date')
    page_number = request.GET.get('page')
    page_obj = paginate(posts, page_number)
    print(page_obj)
    # информация о текущем пользователе доступна в переменной request.user
    context = {
        'user': user,
        'follows': follows,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    user = request.user
    author = get_object_or_404(User, username=username)
    following = user.follower.filter(author=author).all()
    print(user.follower.all())
    if author != user and len(following) == 0:
        Follow.objects.create(user_id=request.user.id,
                              author_id=author.id)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    following = user.follower.filter(author=author).first()
    print(user.follower.all())
    if following:
        following.delete()
    return redirect('posts:follow_index')
