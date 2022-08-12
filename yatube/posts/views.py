from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm
from .utils import get_page


def index(request):
    template = 'posts/index.html'
    page_obj = get_page(Post.objects.all(), request)
    context = {'page_obj': page_obj}
    return render(request, template, context, page_obj)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    page_obj = get_page(group.posts.all(), request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context, page_obj)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = get_page(posts, request)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, template, context, page_obj)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/post_create.html'
    form = PostForm(request.POST or None, files=request.FILES or None,)
    context = {
        'form': form
    }
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    templates = 'posts:post_detail'
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect(templates, post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect(templates, post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    template = 'posts:post_detail'
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return redirect(template, post_id=post_id)
    comment = form.save(commit=False)
    comment.post = post
    comment.author = request.user
    comment.save()
    return redirect(template, post_id=post.id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts = Post.objects.filter(
        author__following__user=request.user
    )
    page_obj = get_page(posts, request)
    context = {
        'page_obj': page_obj,
        'posts': posts
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(author=author, user=request.user)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user, author__username=username).delete()
    return redirect("posts:profile", username)
