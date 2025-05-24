from django.contrib import auth
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from app.models import Profile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from app.forms import LoginForm, RegisterForm, ProfileEditForm, QuestionForm, AnswerForm
from app.models import Question, Answer, Tag, QuestionLike, AnswerLike
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

    if request.user.is_authenticated:
        question_votes = {}
        for question in page.object_list:
            question_votes[question.id] = question.get_user_vote(request.user)
        context['question_votes'] = question_votes
    
    return render(request, 'index.html', context=context)

@login_required
def ask(request):
    context = base_context()
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        
        if form.is_valid():
            question = form.save(author=request.user)
            print(f"Question '{question.title}' created by user {request.user.username}")
            return redirect('single_question', question_id=question.id)
        else:
            print(f"Question creation error: {form.errors}")
            
        context['form'] = form
    else:
        context['form'] = QuestionForm()
    
    return render(request, 'ask.html', context=context)

def login(request):
    context = base_context()
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            user = form.cleaned_data['user']
            username = form.cleaned_data['username']
            
            auth.login(request, user)
            print(f"User {username} successfully logged in")

            continue_url = (request.POST.get('continue') or 
                          request.GET.get('continue') or 
                          request.POST.get('next') or 
                          request.GET.get('next'))
            if continue_url:
                return redirect(continue_url)
            else:
                return redirect('profile_edit')
        else:
            print(f"Login error: {form.non_field_errors()}")
            
        context['form'] = form
    else:
        context['form'] = LoginForm()

    context['continue'] = request.GET.get('continue') or request.GET.get('next', '')
    
    return render(request, 'login.html', context=context)

def register(request):
    context = base_context()
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            print(f"User {username} successfully registered")

            auth.login(request, user)
            return redirect('index')
        else:
            print(f"Registration error: {form.errors}")
            
        context['form'] = form
    else:
        context['form'] = RegisterForm()
    
    return render(request, 'register.html', context=context)

def single_question(request, question_id):
    question = get_object_or_404(Question, id=question_id, is_active=True)
    answers = Answer.objects.for_question_with_author(question_id)
    page = paginate(answers, request)
    
    context = base_context()
    context.update({
        'question': question, 
        'answers': page.object_list, 
        'page_obj': page
    })

    if request.user.is_authenticated:
        context['question_user_vote'] = question.get_user_vote(request.user)

        answer_votes = {}
        for answer in page.object_list:
            answer_votes[answer.id] = answer.get_user_vote(request.user)
        context['answer_votes'] = answer_votes

    if request.user.is_authenticated:
        if request.method == 'POST':
            form = AnswerForm(request.POST)
            
            if form.is_valid():
                answer = form.save(author=request.user, question=question)
                print(f"Answer added by user {request.user.username} to question {question.title}")
                
                return redirect(f'/question/{question_id}#{answer.id}')
            else:
                print(f"Answer creation error: {form.errors}")
                
            context['answer_form'] = form
        else:
            context['answer_form'] = AnswerForm()
    
    return render(request, 'single_question.html', context=context)

def hot(request):
    tags = Tag.objects.popular_tags()
    questions = Question.objects.best_questions()
    page = paginate(questions, request)
    context = base_context()
    context.update({'questions': page.object_list, 'page_obj': page})

    if request.user.is_authenticated:
        question_votes = {}
        for question in page.object_list:
            question_votes[question.id] = question.get_user_vote(request.user)
        context['question_votes'] = question_votes
    
    return render(request, 'hot.html', context=context)

def tag(request, tag_name):
    tags = Tag.objects.popular_tags()
    questions = Question.objects.with_tag(tag_name)
    page = paginate(questions, request)
    context = base_context()
    context.update({'questions': page.object_list, 'page_obj': page, 'tag_name': tag_name})

    if request.user.is_authenticated:
        question_votes = {}
        for question in page.object_list:
            question_votes[question.id] = question.get_user_vote(request.user)
        context['question_votes'] = question_votes
    
    return render(request, 'tag.html', context=context)

def logout(request):
    auth.logout(request)
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def profile_edit(request):
    context = base_context()

    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={'avatar': 'placeholder.png'}
    )
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        
        if form.is_valid():
            form.save()
            print(f"Profile for user {request.user.username} updated")
            return redirect('profile_edit')
        else:
            print(f"Profile update error: {form.errors}")
            
        context['form'] = form
    else:
        context['form'] = ProfileEditForm(instance=profile, user=request.user)
    
    # Добавляем профиль в контекст для отображения текущего аватара
    context['profile'] = profile
    
    return render(request, 'profile_edit.html', context=context)

@require_POST
@login_required
@csrf_protect
def vote_question(request):
    try:
        question_id = request.POST.get('question_id')
        vote_type = request.POST.get('vote_type')
        
        if not question_id or vote_type not in ['like', 'dislike']:
            return JsonResponse({'error': 'Invalid parameters'}, status=400)
        
        question = get_object_or_404(Question, id=question_id)
        is_positive = vote_type == 'like'

        existing_like = QuestionLike.objects.filter(
            user=request.user, 
            question=question
        ).first()
        
        if existing_like:
            if existing_like.is_positive == is_positive:
                existing_like.delete()
            else:
                existing_like.is_positive = is_positive
                existing_like.save()
        else:
            QuestionLike.objects.create(
                user=request.user,
                question=question,
                is_positive=is_positive
            )

        new_rating = question.rating()
        
        return JsonResponse({
            'success': True,
            'new_rating': new_rating
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
@login_required
@csrf_protect
def vote_answer(request):
    try:
        answer_id = request.POST.get('answer_id')
        vote_type = request.POST.get('vote_type')  # 'like' или 'dislike'
        
        if not answer_id or vote_type not in ['like', 'dislike']:
            return JsonResponse({'error': 'Invalid parameters'}, status=400)
        
        answer = get_object_or_404(Answer, id=answer_id)
        is_positive = vote_type == 'like'

        existing_like = AnswerLike.objects.filter(
            user=request.user, 
            answer=answer
        ).first()
        
        if existing_like:
            if existing_like.is_positive == is_positive:
                existing_like.delete()
            else:
                existing_like.is_positive = is_positive
                existing_like.save()
        else:
            AnswerLike.objects.create(
                user=request.user,
                answer=answer,
                is_positive=is_positive
            )

        new_rating = answer.total_likes()
        
        return JsonResponse({
            'success': True,
            'new_rating': new_rating
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
@login_required
@csrf_protect
def mark_correct_answer(request):
    try:
        answer_id = request.POST.get('answer_id')
        
        if not answer_id:
            return JsonResponse({'error': 'Answer ID required'}, status=400)
        
        answer = get_object_or_404(Answer, id=answer_id)

        if answer.question.author != request.user:
            return JsonResponse({'error': 'Only question author can mark correct answer'}, status=403)

        Answer.objects.filter(
            question=answer.question,
            is_correct=True
        ).update(is_correct=False)

        answer.is_correct = not answer.is_correct
        answer.save()
        
        return JsonResponse({
            'success': True,
            'is_correct': answer.is_correct
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)