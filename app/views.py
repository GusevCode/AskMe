from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from app.models import Question, Answer, Tag
from askme_gusev import settings

# Create your views here.

BOOTSTRAP_COLORS = ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark",]

def base_context():
    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'popular_tags': Tag.objects.popular_tags(10),
        'bootstrap_colors': BOOTSTRAP_COLORS
    }

def paginate(objects_list, request, per_page=5):
    page_num = request.GET.get('page')
    paginator = Paginator(objects_list, per_page)
    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page
def index(request):
    questions = Question.objects.get_all()
    page = paginate(questions, request)
    context = base_context()
    context.update({'questions': page.object_list, 'page_obj': page})
    return render(request, 'index.html', context=context)

def ask(request):
    tags = Tag.objects.popular_tags()
    context = base_context()
    return render(request, 'ask.html', context=context)

def login(request):
    tags = Tag.objects.popular_tags()
    context = base_context()
    return render(request, 'login.html', context=context)

def register(request):
    tags = Tag.objects.popular_tags()
    context = base_context()
    return render(request, 'register.html', context=context)

def single_question(request, question_id):
    tags = Tag.objects.popular_tags()
    answers = Answer.objects.for_question_with_author(question_id)
    question = Question.objects.get(id=question_id)
    page = paginate(answers, request)
    context = base_context()
    context.update({'question': question, "answers": page.object_list, 'page_obj': page})
    return render(request, 'single_question.html', context=context)

def settings_page(request):
    tags = Tag.objects.popular_tags()
    context = base_context()
    return render(request, 'settings.html', context=context)

def hot(request):
    tags = Tag.objects.popular_tags()
    questions = Question.objects.best_questions()
    page = paginate(questions, request)
    context = base_context()
    context.update({'questions': page.object_list, 'page_obj': page})
    return render(request, 'hot.html', context=context)

def tag(request, tag_name):
    tags = Tag.objects.popular_tags()
    questions = Question.objects.with_tag(tag_name)
    page = paginate(questions, request)
    context = base_context()
    context.update({'questions': page.object_list, 'page_obj': page, 'tag_name': tag_name})
    return render(request, 'tag.html', context=context)