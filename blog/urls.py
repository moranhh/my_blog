from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),
    path('posts/<int:pk>/', views.detail, name='detail'),
    path('archives/<int:year>/<int:month>/', views.ArchiveView.as_view(), name='archive'),
    path('categories/<int:pk>/', views.CategoryView.as_view(), name='category'),
    path('tags/<int:pk>/', views.TagView.as_view(), name='tag'),
    path('search/', views.search, name='search'),
    path('python/', views.python, name='python'),
    path('c/', views.c, name='c'),
    path('linux/', views.linux, name='linux'),
    path('algorithm/', views.algorithm, name='algorithm'),
    path('db/', views.db, name='db'),
    path('someelse/', views.someelse, name='someelse'),
]