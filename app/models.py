from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Sum

from askme_gusev import settings

# Managers

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=username,
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        Profile.objects.create(
            user=user,
            avatar='placeholder.png'
        )
        return user


class TagManager(models.Manager):
    def get_or_create(self, name):
        try:
            tag = self.get(name__iexact=name)
            return tag, False
        except self.model.DoesNotExist:
            tag = self.create(name=name)
            return tag, True

    def popular_tags(self, count=10):
        return self.annotate(
            num_questions=Count('question', distinct=True)
        ).order_by('-num_questions')[:count]


class QuestionManager(models.Manager):
    def create_question(self, author, title, content):
        return self.create(
            author=author,
            title=title,
            content=content,
            is_active=True
        )

    def get_all(self):
        return self.filter(is_active=True).select_related('author').prefetch_related('tags')

    def best_questions(self):
        return self.annotate(
            rating=Count('questionlike', filter=models.Q(questionlike__is_positive=True)) -
                   Count('questionlike', filter=models.Q(questionlike__is_positive=False))
        ).order_by('-rating')

    def with_tag(self, tag_name):
        return self.filter(
            is_active=True,
            tags__name__iexact=tag_name
        ).select_related('author').prefetch_related('tags')


class AnswerManager(models.Manager):
    def create_answer(self, author, question, content):
        return self.create(
            author=author,
            question=question,
            content=content
        )

    def for_question(self, question_id):
        return self.filter(question_id=question_id).annotate(
            rating=Count('answerlike', filter=models.Q(answerlike__is_positive=True)) -
                   Count('answerlike', filter=models.Q(answerlike__is_positive=False))
        ).order_by('-rating', '-created_at')

    def for_question_with_author(self, question_id):
        return self.for_question(question_id).select_related('author', 'author__profile')

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/placeholder.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color_class = models.CharField(max_length=20, blank=True, default='bg-primary')

    objects = TagManager()

    def __str__(self):
        return self.name


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    is_active = models.BooleanField(default=True)

    objects = QuestionManager()

    def __str__(self):
        return self.title

    def rating(self):
        return self.questionlike_set.filter(is_positive=True).count() - self.questionlike_set.filter(is_positive=False).count()

    def answer_count(self):
        return self.answer_set.count()



class Answer(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)

    objects = AnswerManager()

    def __str__(self):
        return f"Answer to {self.question.title}"

    def total_likes(self):
        return self.answerlike_set.filter(is_positive=True).count() - self.answerlike_set.filter(is_positive=False).count()

    class Meta:
        ordering = ['-is_correct', '-created_at']

class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_positive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return f"{self.user.username} {'likes' if self.is_positive else 'dislikes'} {self.question.title}"


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_positive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'answer')

    def __str__(self):
        return f"{self.user.username} {'likes' if self.is_positive else 'dislikes'} answer to {self.answer.question.title}"