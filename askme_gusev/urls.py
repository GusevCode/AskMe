"""
URL configuration for askme_gusev project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
# 30 минут по умолчанию
from app import views

urlpatterns = [
    path('', views.index, name="index"),
    path('ask/', views.ask, name="ask"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('signup/', views.register, name="register"),
    path('profile/edit/', views.profile_edit, name="profile_edit"),
    path('question/<int:question_id>', views.single_question, name="single_question"),
    path('hot/', views.hot, name="hot"),
    path('tag/<tag_name>', views.tag, name="tag"),
    
    # AJAX views
    path('ajax/vote-question/', views.vote_question, name='vote_question'),
    path('ajax/vote-answer/', views.vote_answer, name='vote_answer'),
    path('ajax/mark-correct/', views.mark_correct_answer, name='mark_correct_answer'),
    path('ajax/search/', views.search_questions, name='search_questions'),
    path('ajax/test-centrifugo/', views.test_centrifugo, name='test_centrifugo'),
    
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
