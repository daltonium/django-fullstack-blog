from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.http import HttpResponseForbidden

from .models import Post, Category, Tag, Comment
from .forms import PostForm, CommentForm, SearchForm


# ── Helper: base published queryset (reused everywhere) ──
def published_posts():
    return (
        Post.objects
        .filter(status=Post.STATUS_PUBLISHED)
        .select_related('author', 'category')
        .prefetch_related('tags')
    )


# ── Helper: pagination (reused everywhere) ──
def paginate(request, queryset, per_page=8):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


# ── Homepage ──
def post_list(request):
    posts = published_posts()
    categories = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:8]
    popular_posts = published_posts().order_by('-view_count')[:5]
    popular_tags = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:20]
    page_obj = paginate(request, posts)

    return render(request, 'blog/post_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'popular_posts': popular_posts,
        'popular_tags': popular_tags,
        'search_form': SearchForm(),
    })


# ── Single Post ──
def post_detail(request, slug):
    post = get_object_or_404(
        Post.objects
        .select_related('author', 'category')
        .prefetch_related('tags', 'comments__author', 'comments__replies__author'),
        slug=slug,
        status=Post.STATUS_PUBLISHED,
    )
    post.increment_view()

    top_comments = post.comments.filter(
        is_approved=True, parent=None
    ).select_related('author').prefetch_related('replies__author')

    comment_form = CommentForm()

    related_posts = (
        published_posts()
        .filter(category=post.category)
        .exclude(pk=post.pk)[:3]
    )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Please log in to comment.')
            return redirect('users:login')

        comment_form = CommentForm(request.POST)
        parent_id = request.POST.get('parent_id')

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            if parent_id:
                comment.parent = get_object_or_404(Comment, pk=parent_id)
            comment.save()
            messages.success(request, 'Comment posted!')
            return redirect(post.get_absolute_url())

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'top_comments': top_comments,
        'comment_form': comment_form,
        'related_posts': related_posts,
    })


# ── Category Page ──
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = published_posts().filter(category=category)
    page_obj = paginate(request, posts)
    return render(request, 'blog/category_detail.html', {
        'category': category,
        'page_obj': page_obj,
    })


# ── Tag Page ──
def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = published_posts().filter(tags=tag)
    page_obj = paginate(request, posts)
    return render(request, 'blog/tag_detail.html', {
        'tag': tag,
        'page_obj': page_obj,
    })


# ── Search ──
def search_posts(request):
    form = SearchForm(request.GET)
    posts = Post.objects.none()
    query = ''

    if form.is_valid():
        query = form.cleaned_data['q']
        posts = (
            published_posts()
            .filter(
                Q(title__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(body__icontains=query) |
                Q(tags__name__icontains=query) |
                Q(category__name__icontains=query)
            )
            .distinct()
        )

    page_obj = paginate(request, posts)
    return render(request, 'blog/search.html', {
        'form': form,
        'page_obj': page_obj,
        'query': query,
    })


# ── Create Post ──
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            if post.status == Post.STATUS_PUBLISHED:
                post.published_at = timezone.now()
            post.save()
            form.save()
            messages.success(request, 'Post created successfully!')
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form, 'action': 'Create'})


# ── Edit Post ──
@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden('You are not allowed to edit this post.')

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)
            if updated_post.status == Post.STATUS_PUBLISHED and not updated_post.published_at:
                updated_post.published_at = timezone.now()
            updated_post.save()
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect(updated_post.get_absolute_url())
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_form.html', {'form': form, 'action': 'Edit', 'post': post})


# ── Delete Post ──
@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.author != request.user and not request.user.is_staff:
        return HttpResponseForbidden('You are not allowed to delete this post.')

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted.')
        return redirect('blog:post_list')

    return render(request, 'blog/post_confirm_delete.html', {'post': post})


# ── My Posts Dashboard ──
@login_required
def my_posts(request):
    posts = (
        Post.objects
        .filter(author=request.user)
        .select_related('category')
        .prefetch_related('tags')
        .order_by('-created_at')
    )
    page_obj = paginate(request, posts)
    return render(request, 'blog/my_posts.html', {'page_obj': page_obj})
