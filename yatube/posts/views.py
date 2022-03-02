from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Group, Post, User
from .paginator import get_paginator


def index(request):
    post_list = Post.objects.all()
    page_obj = get_paginator(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = get_paginator(post_list, request)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    post_count = author.posts.count()
    page_obj = get_paginator(post_list, request)
    context = {
        'page_obj': page_obj,
        'author': author,
        'post_count': post_count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            author = request.user
            post = form.save(commit=False)
            post.author = author
            post.save()
            username = author.username
            return redirect('posts:profile', username)
    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'POST':
        if request.user != post.author:
            return redirect('posts:post_detail', post_id)
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(
        request, 'posts/post_create.html',
        {
            'form': form,
            'post': post
        }
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
