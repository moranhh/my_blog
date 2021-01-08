#该脚本添加于登录界面之前
import os
import pathlib
import random
import sys
from datetime import timedelta

import django
import faker
from django.utils import timezone

# 将项目根目录添加到 Python 的模块搜索路径中
back = os.path.dirname
BASE_DIR = back(back(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blogproject.settings")
    django.setup()  #只有在 django 启动后，我们才能使用 django 的 ORM 系统。

    from blog.models import Category, Post, Tag
    from comments.models import Comment
    from django.contrib.auth.models import User

    print('clean database')
    Post.objects.all().delete()
    Category.objects.all().delete()
    Tag.objects.all().delete()
    Comment.objects.all().delete()
    User.objects.all().delete()

    print('create a blog user')
    user = User.objects.create_superuser('admin', 'admin@hellogithub.com', 'admin')

    category_list = ['Python学习笔记', '开源项目', '工具资源', '程序员生活感悟', 'test category']
    tag_list = ['django', 'Python', 'Pipenv', 'Docker', 'Nginx', 'Elasticsearch', 'Gunicorn', 'Supervisor', 'test tag']
    a_year_ago = timezone.now() - timedelta(days=365)

    print('create categories and tags')
    for cate in category_list:
        Category.objects.create(name=cate)

    for tag in tag_list:
        Tag.objects.create(name=tag)
    
    #简单地使用 django 的 ORM API 生成博客用户、分类、标签以及一篇 Markdown 测试文章。
    print('create a markdown sample post')
    Post.objects.create(
        title='Markdown 与代码高亮测试',
        body=pathlib.Path(BASE_DIR).joinpath('scripts', 'md.sample').read_text(encoding='utf-8'),
        category=Category.objects.create(name='Markdown测试'),
        author=user,
    )

    print('create some faked posts published within the past year')
    fake = faker.Faker()  # English
    for _ in range(100):
        tags = Tag.objects.order_by('?') #返回随机排序的结果
        tag1 = tags.first()
        tag2 = tags.last()
        cate = Category.objects.order_by('?').first()
        '''
        这里设置起始日期为 1 年前（-1y），终止日期为当下（now），时区为 get_current_timezone 返回的时区，
        这个函数是 django.utils.timezone 模块的辅助函数，它会根据 django 设置文件中 TIME_ZONE 的值返回对应的时区对象。
        '''
        created_time = fake.date_time_between(start_date='-1y', end_date="now",
                                              tzinfo=timezone.get_current_timezone())
        post = Post.objects.create(
            title=fake.sentence().rstrip('.'),
            #Markdown 中只有 2 个换行符分隔的文本才会被解析为段落。
            body='\n\n'.join(fake.paragraphs(10)),
            created_time=created_time,
            category=cate,
            author=user,
        )
        post.tags.add(tag1, tag2)
        post.save()

    fake = faker.Faker('zh_CN') #生成中文数据
    for _ in range(100):  # Chinese
        tags = Tag.objects.order_by('?')
        tag1 = tags.first()
        tag2 = tags.last()
        cate = Category.objects.order_by('?').first()
        created_time = fake.date_time_between(start_date='-1y', end_date="now",
                                              tzinfo=timezone.get_current_timezone())
        post = Post.objects.create(
            title=fake.sentence().rstrip('.'),
            body='\n\n'.join(fake.paragraphs(10)),
            created_time=created_time,
            category=cate,
            author=user,
        )
        post.tags.add(tag1, tag2)
        post.save()

    print('create some comments')
    for post in Post.objects.all()[:20]:
        post_created_time = post.created_time
        #评论的发布时间必须位于被评论文章的发布时间和当前时间之间
        delta_in_days = '-' + str((timezone.now() - post_created_time).days) + 'd'
        for _ in range(random.randrange(3, 15)):
            Comment.objects.create(
                name=fake.name(),
                email=fake.email(),
                url=fake.uri(),
                text=fake.paragraph(),
                created_time=fake.date_time_between(
                     start_date=delta_in_days, 
                     end_date="now", 
                     tzinfo=timezone.get_current_timezone()),
                post=post,
            )

    print('done!')