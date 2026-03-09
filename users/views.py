from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from blog.models import Post


def register(request):
    if request.user.is_authenticated:
        return redirect('blog:post_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('blog:post_list')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('blog:post_list')
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'blog:post_list')
            return redirect(next_url)
        messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('blog:post_list')


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = (
        Post.objects
        .filter(author=author, status='published')
        .select_related('category')
        .prefetch_related('tags')
        .order_by('-published_at')
    )
    return render(request, 'users/profile.html', {'author': author, 'posts': posts})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('users:profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})
