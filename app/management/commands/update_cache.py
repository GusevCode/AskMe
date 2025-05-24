from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from app.models import Tag, Profile, Question, Answer


class Command(BaseCommand):
    help = 'Update cache for popular tags and best users'

    def handle(self, *args, **options):
        self.stdout.write('Updating cache...')

        try:
            three_months_ago = timezone.now() - timedelta(days=90)
            popular_tags = list(Tag.objects.annotate(
                num_questions=Count(
                    'question', 
                    filter=Q(
                        question__is_active=True,
                        question__created_at__gte=three_months_ago
                    )
                )
            ).filter(num_questions__gt=0).order_by('-num_questions')[:10])
            
            cache.set('popular_tags', popular_tags, 60 * 60 * 24)  # 24 часа
            self.stdout.write(
                self.style.SUCCESS(f'Updated popular_tags cache with {len(popular_tags)} tags')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating popular_tags: {e}')
            )
        try:
            one_week_ago = timezone.now() - timedelta(days=7)

            question_authors = Profile.objects.select_related('user').annotate(
                total_question_likes=Count(
                    'user__question__questionlike',
                    filter=Q(
                        user__question__is_active=True,
                        user__question__created_at__gte=one_week_ago,
                        user__question__questionlike__is_positive=True
                    )
                ),
                total_answer_likes=Count(
                    'user__answer__answerlike',
                    filter=Q(
                        user__answer__created_at__gte=one_week_ago,
                        user__answer__answerlike__is_positive=True
                    )
                )
            ).annotate(
                total_activity=Count('user__question', filter=Q(
                    user__question__is_active=True,
                    user__question__created_at__gte=one_week_ago
                )) + Count('user__answer', filter=Q(
                    user__answer__created_at__gte=one_week_ago
                ))
            ).filter(
                Q(total_question_likes__gt=0) | 
                Q(total_answer_likes__gt=0) | 
                Q(total_activity__gt=0)
            ).order_by('-total_question_likes', '-total_answer_likes', '-total_activity')[:10]

            best_users = list(question_authors)
            
            cache.set('best_users', best_users, 60 * 60 * 24)  # 24 часа
            self.stdout.write(
                self.style.SUCCESS(f'Updated best_users cache with {len(best_users)} users')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating best_users: {e}')
            )

        self.stdout.write(self.style.SUCCESS('Cache update completed!')) 