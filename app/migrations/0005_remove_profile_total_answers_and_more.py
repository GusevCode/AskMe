# Generated by Django 5.2 on 2025-04-06 17:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_answer_options_profile_total_answers_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='total_answers',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='total_questions',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='total_rating',
        ),
    ]
