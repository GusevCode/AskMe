from django.contrib import auth, messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.cache import cache
from app.models import Profile
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from app.forms import LoginForm, RegisterForm, ProfileEditForm, QuestionForm, AnswerForm
from app.models import Question, Answer, Tag, QuestionLike, AnswerLike
from askme_gusev import settings

# Create your views here.

BOOTSTRAP_COLORS = ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark"]

def base_context():
    popular_tags = cache.get('popular_tags')
    if popular_tags is None:
        try:
            popular_tags = list(Tag.objects.popular_tags(10))
            cache.set('popular_tags', popular_tags, 60 * 30)  # 30 minutes
        except Exception as e:
            print(f"Error loading popular tags: {e}")
            popular_tags = []

    best_users = cache.get('best_users')
    if best_users is None:
        try:
            best_users = list(Profile.objects.best_users(5))
            cache.set('best_users', best_users, 60 * 15)  # 15 minutes
        except Exception as e:
            print(f"Error loading best users, trying alternative: {e}")
            try:
                best_users = list(Profile.objects.best_users_by_activity(5))
                cache.set('best_users', best_users, 60 * 15)
            except Exception as e2:
                print(f"Error loading best users alternative: {e2}")
                best_users = []
    
    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'popular_tags': popular_tags,
        'best_users': best_users,
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
            messages.success(request, f'Question "{question.title}" has been successfully created!')
            print(f"Question '{question.title}' created by user {request.user.username}")

            cache.delete('popular_tags')
            
            return redirect('single_question', question_id=question.id)
        else:
            messages.error(request, 'Question was not created. Please fix the errors in the form.')
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
            messages.success(request, f'Welcome back, {username}!')
            print(f"User {username} successfully logged in")

            continue_url = (request.POST.get('continue') or 
                          request.GET.get('continue') or 
                          request.POST.get('next') or 
                          request.GET.get('next'))
            if continue_url:
                return redirect(continue_url)
            else:
                return redirect('index')
        else:
            messages.error(request, 'Login failed. Please check your username and password.')
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
            messages.success(request, f'Registration successful! Welcome, {username}!')
            print(f"User {username} successfully registered")

            auth.login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Registration failed. Please fix the errors in the form.')
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
                messages.success(request, 'Answer has been successfully added!')
                print(f"Answer added by user {request.user.username} to question {question.title}")

                cache.delete('hot_questions')
                
                return redirect(f'/question/{question_id}#{answer.id}')
            else:
                messages.error(request, 'Answer was not added. Please fix the errors in the form.')
                print(f"Answer creation error: {form.errors}")
                
            context['answer_form'] = form
        else:
            context['answer_form'] = AnswerForm()
    
    return render(request, 'single_question.html', context=context)

def hot(request):
    hot_questions = cache.get('hot_questions')
    if hot_questions is None:
        try:
            hot_questions = list(Question.objects.best_questions())
            cache.set('hot_questions', hot_questions, 60 * 10)  # 10 minutes
            print(f"Loaded {len(hot_questions)} hot questions with rating logic")
        except Exception as e:
            print(f"Error loading hot questions: {e}")
            try:
                hot_questions = list(Question.objects.filter(
                    is_active=True
                ).exclude(
                    answer__is_correct=True
                ).select_related('author', 'author__profile').prefetch_related('tags').order_by('-created_at')[:50])
                cache.set('hot_questions', hot_questions, 60 * 5)
                print(f"Fallback: loaded {len(hot_questions)} unsolved questions")
            except Exception as e2:
                print(f"Error loading fallback hot questions: {e2}")
                hot_questions = list(Question.objects.get_all()[:50])
                cache.set('hot_questions', hot_questions, 60 * 2)
                print(f"Final fallback: loaded {len(hot_questions)} new questions")
    
    page = paginate(hot_questions, request)
    context = base_context()
    context.update({'questions': page.object_list, 'page_obj': page})

    if request.user.is_authenticated:
        question_votes = {}
        for question in page.object_list:
            question_votes[question.id] = question.get_user_vote(request.user)
        context['question_votes'] = question_votes
    
    return render(request, 'hot.html', context=context)

def tag(request, tag_name):
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
    username = request.user.username if request.user.is_authenticated else "user"
    auth.logout(request)
    messages.info(request, f'Goodbye, {username}!')
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
            messages.success(request, 'Profile has been successfully updated!')
            print(f"Profile for user {request.user.username} updated")
            return redirect('profile_edit')
        else:
            messages.error(request, 'Profile update failed. Please fix the errors in the form.')
            print(f"Profile update error: {form.errors}")
            
        context['form'] = form
    else:
        context['form'] = ProfileEditForm(instance=profile, user=request.user)

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

        cache.delete('hot_questions')
        
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

        cache.delete('hot_questions')
        
        return JsonResponse({
            'success': True,
            'is_correct': answer.is_correct
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)