from django.urls import path
from . import views

app_name = 'blog'   # ← this line is what was missing

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('search/', views.search_posts, name='search'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('create/', views.post_create, name='post_create'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('tag/<slug:slug>/', views.tag_detail, name='tag_detail'),
    path('<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('<slug:slug>/delete/', views.post_delete, name='post_delete'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
]
