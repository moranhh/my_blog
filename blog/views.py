from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Tag
import mistune, markdown, re
from markdown.extensions.toc import TocExtension
from django.utils.text import slugify
# Create your views here.
from django.http import HttpResponse
from django.views.generic import ListView, DetailView #使用类视图 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from pure_pagination import PaginationMixin
from django.db.models import Q
from django.contrib import messages

'''
def index(request, pg):
    post_list = Post.objects.all()
    return render(request, 'blog/index.html', context={'post_list': post_list})
'''
class IndexView(PaginationMixin, ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    # 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = 6


def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    #调用了该函数 文章被访问 阅读量+1
    post.increase_views()

    #确认登录状态
    if request.session.get('is_login', None):
        post.is_login = True
        post.commenter_name = request.session.get('user_name')  #获取登录名
    
    #extensions 中的 toc 拓展不再是字符串 markdown.extensions.toc ，而是 TocExtension 的实例。
    #TocExtension 在实例化时其 slugify 参数可以接受一个函数，这个函数将被用于处理标题的锚点值。
    #Markdown 内置的处理方法不能处理中文标题，所以我们使用了 django.utils.text 中的 slugify 方法，该方法可以很好地处理中文。
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

'''
class PostDetailView(DetailView):
    # 这些属性的含义和 ListView 是一样的
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次，就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法，是因为只有当 get 方法被调用后，
        # 才有 self.object 属性，其值为 Post 模型实例，即被访问的文章 post
        response = super(PostDetailView, self).get(request, *args, **kwargs)

        # 将文章阅读量 +1 注意 self.object 的值就是被访问的文章 post
        self.object.increase_views()

        # 视图必须返回一个 HttpResponse 对象
        return response

    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
        post = super().get_object(queryset=None)
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            TocExtension(slugify=slugify),
        ])
        post.body = md.convert(post.body)

        m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
        post.toc = m.group(1) if m is not None else ''

        return post
'''
'''
def archive(request, year, month):  #归档视图
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    )
    return render(request, 'blog/index.html', context={'post_list': post_list})
'''
class ArchiveView(IndexView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    def get_queryset(self):
        return super(ArchiveView, self).get_queryset().filter(created_time__year=self.kwargs.get('year'), 
                                                            created_time__month=self.kwargs.get('month'))
    # 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = 6
'''
def category(request, pk):  #分类视图
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})
'''
class CategoryView(IndexView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryView, self).get_queryset().filter(category=cate)
    # 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = 6

'''
def tag(request, pk):
    # 记得在开始部分导入 Tag 类
    t = get_object_or_404(Tag, pk=pk)
    post_list = Post.objects.filter(tags=t)
    return render(request, 'blog/index.html', context={'post_list': post_list})
'''
class TagView(IndexView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    def get_queryset(self):
        t = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=t)
    # 指定 paginate_by 属性后开启分页功能，其值代表每一页包含多少篇文章
    paginate_by = 6

def search(request):
    q = request.GET.get('q')

    if not q:
        error_msg = "请输入搜索关键词"
        messages.add_message(request, messages.ERROR, error_msg, extra_tags='danger')
        return redirect('blog:index')

    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render(request, 'blog/index.html', {'post_list': post_list})

class PythonView(IndexView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    def get_queryset(self):
        cate = get_object_or_404(Category, name='python')
        return super(PythonView, self).get_queryset().filter(category=cate)
    paginate_by = 6
'''
def python(request):  #header跳转视图
    cate = get_object_or_404(Category, name='python')
    post_list = Post.objects.filter(category=cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})
'''
class CView(IndexView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    def get_queryset(self):
        cate = get_object_or_404(Category, name='c++')
        return super(CView, self).get_queryset().filter(category=cate)
    paginate_by = 6
'''
def c(request):  #header跳转视图
    cate = get_object_or_404(Category, name='c++')
    post_list = Post.objects.filter(category=cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})
'''
class LinuxView(IndexView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    def get_queryset(self):
        cate = get_object_or_404(Category, name='linux')
        return super(LinuxView, self).get_queryset().filter(category=cate)
    paginate_by = 6
'''
def linux(request):  #header跳转视图
    cate = get_object_or_404(Category, name='linux')
    post_list = Post.objects.filter(category=cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})
'''
class AlgorithmView(IndexView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    def get_queryset(self):
        cate = get_object_or_404(Category, name='算法')
        return super(AlgorithmView, self).get_queryset().filter(category=cate)
    paginate_by = 6
'''
def algorithm(request):  #header跳转视图
    cate = get_object_or_404(Category, name='算法')
    post_list = Post.objects.filter(category=cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})
'''
class DbView(IndexView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    def get_queryset(self):
        cate = get_object_or_404(Category, name='数据库')
        return super(DbView, self).get_queryset().filter(category=cate)
    paginate_by = 6
'''
def db(request):  #header跳转视图
    cate = get_object_or_404(Category, name='数据库')
    post_list = Post.objects.filter(category=cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})
'''
class SomeelseView(IndexView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    def get_queryset(self):
        cate = get_object_or_404(Category, name='其他')
        return super(SomeelseView, self).get_queryset().filter(category=cate)
    paginate_by = 6
'''
def someelse(request):  #header跳转视图
    cate = get_object_or_404(Category, name='其他')
    post_list = Post.objects.filter(category=cate)
    return render(request, 'blog/index.html', context={'post_list': post_list})
'''