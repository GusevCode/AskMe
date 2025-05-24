from django import template
from django.core.cache import cache
from app.models import Tag, Profile

register = template.Library()


@register.inclusion_tag('includes/popular_tags.html')
def show_popular_tags():
    popular_tags = cache.get('popular_tags')
    if popular_tags is None:
        try:
            popular_tags = list(Tag.objects.popular_tags(10))
            cache.set('popular_tags', popular_tags, 60 * 30)  # 30 минут
        except Exception:
            popular_tags = []
    
    return {'popular_tags': popular_tags}


@register.inclusion_tag('includes/best_users.html')
def show_best_users():
    best_users = cache.get('best_users')
    if best_users is None:
        try:
            best_users = list(Profile.objects.best_users(5))
            cache.set('best_users', best_users, 60 * 15)  # 15 минут
        except Exception:
            best_users = []
    
    return {'best_users': best_users} 