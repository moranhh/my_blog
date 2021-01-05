from django.shortcuts import render, get_object_or_404
from .models import Post, Category, Tag
import mistune, markdown, re
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify
# Create your views here.
from django.http import HttpResponse


def index(request):
    post_list = Post.objects.all()
    return render(request, 'blog/index.html', context={'post_list': post_list})
    
def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    '''
        extensions 中的 toc 拓展不再是字符串 markdown.extensions.toc ，而是 TocExtension 的实例。
        TocExtension 在实例化时其 slugify 参数可以接受一个函数，这个函数将被用于处理标题的锚点值。
        Markdown 内置的处理方法不能处理中文标题，所以我们使用了 django.utils.text 中的 slugify 方法，该方法可以很好地处理中文。
    '''
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
        TocExtension(slugify=slugify),
    ])
    post.body = md.convert(post.body)
    #不使用re.S参数，则只在每一行内进行匹配 使用re.S参数以后则在全文进行匹配
    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S) 
    post.toc = m.group(1) if m is not None else ''
    #post.body = mistune.markdown(post.body)    
    return render(request, 'blog/detail.html', context={'post': post})

def archive(request, year, month):  #归档视图
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    )
    return render(request, 'blog/index.html', context={'post_list': post_list})

def category(request, pk):  #分类视图
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})

def tag(request, pk):
    # 记得在开始部分导入 Tag 类
    t = get_object_or_404(Tag, pk=pk)
    post_list = Post.objects.filter(tags=t)
    return render(request, 'blog/index.html', context={'post_list': post_list})