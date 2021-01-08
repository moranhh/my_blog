from django.contrib import admin

# Register your models here.
from .models import Comment


class CommentAdmin(admin.ModelAdmin):
    #list_display = ['name', 'email', 'url', 'post', 'created_time']
    #fields = ['name', 'email', 'url', 'text', 'post']
    list_display = ['name',  'post', 'created_time']
    fields = ['name', 'text', 'created_time']

admin.site.register(Comment, CommentAdmin)