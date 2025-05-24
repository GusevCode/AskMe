from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Case, When, IntegerField, F
from django.db.models.signals import post_save
from django.dispatch import receiver

from askme_gusev import settings

class TagManager(models.Manager):
    def get_or_create_by_name(self, name):
        try:
            tag = self.get(name__iexact=name)
            return tag, False
        except self.model.DoesNotExist:
            tag = self.create(name=name)
            return tag, True

    def popular_tags(self, count=10):
        return self.annotate(
            num_questions=Count('question', filter=models.Q(question__is_active=True))
        ).filter(num_questions__gt=0).order_by('-num_questions')[:count]


class QuestionManager(models.Manager):
    def create_question(self, author, title, content):
        return self.create(
            author=author,
            title=title,
            content=content,
            is_active=True
        )

    def get_all(self):
        return self.filter(is_active=True).select_related(
            'author', 'author__profile'
        ).prefetch_related('tags').order_by('-created_at')

    def best_questions(self):
        return self.filter(
            is_active=True
        ).select_related(
            'author', 'author__profile'
        ).prefetch_related('tags').annotate(
            rating_score=Count(
                'questionlike', 
                filter=models.Q(questionlike__is_positive=True)
            ) - Count(
                'questionlike', 
                filter=models.Q(questionlike__is_positive=False)
            ),
            has_correct_answer=Count(
                'answer', 
                filter=models.Q(answer__is_correct=True)
            )
        ).filter(
            has_correct_answer=0
        ).order_by(
            '-rating_score',
            '-created_at'
        )[:50]

    def with_tag(self, tag_name):
        return self.filter(
            is_active=True,
            tags__name__iexact=tag_name
        ).select_related(
            'author', 'author__profile'
        ).prefetch_related('tags').order_by('-created_at')[:100]


class AnswerManager(models.Manager):
    def create_answer(self, author, question, content):
        return self.create(
            author=author,
            question=question,
            content=content
        )

    def for_question(self, question_id):
        return self.filter(question_id=question_id).select_related(
            'author', 'author__profile'
        ).order_by('-is_correct', '-created_at')

    def for_question_with_author(self, question_id):
        return self.for_question(question_id)


class ProfileManager(models.Manager):
    def best_users(self, count=5):
        return self.select_related('user').annotate(
            question_count=Count('user__question', filter=models.Q(user__question__is_active=True))
        ).filter(question_count__gt=0).order_by('-question_count')[:count]

    def best_users_by_activity(self, count=5):
        return self.select_related('user').filter(
            user__question__isnull=False
        ).distinct().order_by('-user__date_joined')[:count]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/placeholder.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProfileManager()

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            try:
                return self.avatar.url
            except:
                return f'{settings.MEDIA_URL}placeholder.png'
        else:
            return f'{settings.MEDIA_URL}placeholder.png'
    
    def question_count(self):
        if hasattr(self, 'question_count'):
            return self.question_count
        return self.user.question_set.filter(is_active=True).count()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color_class = models.CharField(max_length=20, blank=True, default='primary')

    objects = TagManager()

    def __str__(self):
        return self.name
    
    def questions_count(self):
        if hasattr(self, 'num_questions'):
            return self.num_questions
        return self.question_set.filter(is_active=True).count()


class Question(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    is_active = models.BooleanField(default=True)

    objects = QuestionManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['author']),
            models.Index(fields=['is_active', '-created_at']),
        ]

    def __str__(self):
        return self.title

    def rating(self):
        return self.questionlike_set.filter(is_positive=True).count() - self.questionlike_set.filter(is_positive=False).count()

    def answer_count(self):
        return self.answer_set.count()
    
    def is_solved(self):
        return self.answer_set.filter(is_correct=True).exists()
    
    def get_rating_score(self):
        if hasattr(self, 'rating_score'):
            return self.rating_score
        return self.rating()
    
    def get_user_vote(self, user):
        if not user.is_authenticated:
            return None
        
        vote = self.questionlike_set.filter(user=user).first()
        if vote:
            return 'like' if vote.is_positive else 'dislike'
        return None


class Answer(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_correct = models.BooleanField(default=False)

    objects = AnswerManager()

    class Meta:
        ordering = ['-is_correct', '-created_at']
        indexes = [
            models.Index(fields=['question']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_correct']),
            models.Index(fields=['question', '-is_correct', '-created_at']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return f"Answer to {self.question.title}"

    def total_likes(self):
        return self.answerlike_set.filter(is_positive=True).count() - self.answerlike_set.filter(is_positive=False).count()
    
    def get_user_vote(self, user):
        if not user.is_authenticated:
            return None
        
        vote = self.answerlike_set.filter(user=user).first()
        if vote:
            return 'like' if vote.is_positive else 'dislike'
        return None


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_positive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')
        indexes = [
            models.Index(fields=['question']),
            models.Index(fields=['user']),
            models.Index(fields=['is_positive']),
            models.Index(fields=['question', 'is_positive']),
        ]

    def __str__(self):
        return f"{self.user.username} {'likes' if self.is_positive else 'dislikes'} {self.question.title}"


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    is_positive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'answer')
        indexes = [
            models.Index(fields=['answer']),
            models.Index(fields=['user']),
            models.Index(fields=['is_positive']),
            models.Index(fields=['answer', 'is_positive']),
        ]

    def __str__(self):
        return f"{self.user.username} {'likes' if self.is_positive else 'dislikes'} answer to {self.answer.question.title}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            avatar='placeholder.png'
        )