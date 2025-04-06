from django.contrib import admin
from django.contrib.auth.models import User

from app.models import Tag, Question, Profile, Answer, QuestionLike, AnswerLike

# Register your models here.
admin.site.register(Profile)
admin.site.register(Tag)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(QuestionLike)
admin.site.register(AnswerLike)





