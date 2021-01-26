from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('posts/<int:pk>/', views.detail, name='detail'),
    path('archives/<int:year>/<int:month>/', views.ArchiveView.as_view(), name='archive'),
    path('categories/<int:pk>/', views.CategoryView.as_view(), name='category'),
    path('tags/<int:pk>/', views.TagView.as_view(), name='tag'),
    path('search/', views.search, name='search'),
    path('python/', views.PythonView.as_view(), name='python'),
    path('c/', views.CView.as_view(), name='c'),
    path('linux/', views.LinuxView.as_view(), name='linux'),
    path('algorithm/', views.AlgorithmView.as_view(), name='algorithm'),
    path('db/', views.DbView.as_view(), name='db'),
    path('someelse/', views.SomeelseView.as_view(), name='someelse'),
]