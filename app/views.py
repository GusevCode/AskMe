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
