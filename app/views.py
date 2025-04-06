from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

QUESTIONS = [
    {
        'title': f'title {i}',
        'id': i,
        'text': f'This is text for question {i}'
    } for i in range(1, 30)
]

def index(request):
    return render(request, 'index.html', context={'questions': QUESTIONS})

def ask(request):
    return render(request, 'ask.html')

def login(request):
    return render(request, 'login.html')

def register(request):
    return render(request, 'register.html')

def single_question(request):
    return render(request, 'single_question.html')

def settings(request):
    return render(request, 'settings.html')
