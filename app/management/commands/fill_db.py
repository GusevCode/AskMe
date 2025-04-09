from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike
from faker import Faker
import random
import os
from django.conf import settings
from django.db import transaction


def get_random_avatar():
    avatar_dir = os.path.join(settings.MEDIA_ROOT, '')

    if not os.path.exists(avatar_dir):
        os.makedirs(avatar_dir)

    avatars = [
        f for f in os.listdir(avatar_dir)
        if os.path.isfile(os.path.join(avatar_dir, f))
    ]
    if avatars:
        return random.choice(avatars)

    return 'placeholder.png'


BOOTSTRAP_COLORS = ["primary", "secondary", "success", "danger", "warning", "info"]
BATCH_SIZE = 2000


class Command(BaseCommand):
    help = "Заполняет тестовыми данными"

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Коэффициент заполнения сущностей')

    def print_progress(self, current, total, entity_name):
        if current % 100 == 0 or current == total:
            self.stdout.write(f"Создано {current} {entity_name} из {total}", ending='\r')
            if current == total:
                self.stdout.write()

    @transaction.atomic
    def handle(self, *args, **kwargs):
        ratio = kwargs['ratio']
        fake = Faker()

        num_users = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_tags = ratio
        num_ratings = ratio * 200

        ent_num = 1

        # Создание пользователей и профилей
        self.stdout.write(f"Создаётся {num_users} пользователей...")
        user_objs = []
        profile_objs = []
        for i in range(1, num_users + 1):
            user = User(
                username=fake.user_name() + str(i) + str(ent_num),
                email=fake.email(),
            )
            ent_num += 1
            user.set_password('password')
            user_objs.append(user)
            self.print_progress(i, num_users, "пользователей")

            profile_objs.append(Profile(user=user, avatar=get_random_avatar()))
            ent_num += 1

            if i % BATCH_SIZE == 0 or i == num_users:
                User.objects.bulk_create(user_objs)
                Profile.objects.bulk_create(profile_objs)
                user_objs = []
                profile_objs = []

        users = list(User.objects.filter(is_superuser=False).order_by('id')[:num_users])

        # Создание тегов
        self.stdout.write(f"Создаётся {num_tags} тэгов...")
        tag_objs = []
        for i in range(1, num_tags + 1):
            tag_objs.append(Tag(
                name=fake.word() + str(i) + str(ent_num),
                color_class=random.choice(BOOTSTRAP_COLORS),
                description=fake.text(max_nb_chars=50)
            ))
            ent_num += 1
            self.print_progress(i, num_tags, "тегов")
            if i % BATCH_SIZE == 0 or i == num_tags:
                Tag.objects.bulk_create(tag_objs)
                tag_objs = []
        tags = list(Tag.objects.all().order_by('id')[:num_tags])

        # Создание вопросов
        self.stdout.write(f"Создаётся {num_questions} вопросов...")
        question_objs = []
        tag_relations = []
        for i in range(1, num_questions + 1):
            question = Question(
                author=random.choice(users),
                title=fake.sentence(nb_words=6),
                content=fake.text(max_nb_chars=200),
                is_active=True
            )
            question_objs.append(question)
            self.print_progress(i, num_questions, "вопросов")

            if i % BATCH_SIZE == 0 or i == num_questions:
                created_questions = Question.objects.bulk_create(question_objs)
                # Подготовка связей many-to-many
                for q in created_questions:
                    num_tags = random.randint(1, 5)
                    for tag in random.sample(tags, min(num_tags, len(tags))):
                        tag_relations.append(Question.tags.through(
                            question_id=q.id,
                            tag_id=tag.id
                        ))
                question_objs = []

        # Массовое создание связей many-to-many
        if tag_relations:
            Question.tags.through.objects.bulk_create(tag_relations)
        questions = list(Question.objects.all().order_by('id')[:num_questions])

        # Создание ответов
        self.stdout.write(f"Создаётся {num_answers} ответов...")
        answer_objs = []
        for i in range(1, num_answers + 1):
            answer_objs.append(Answer(
                author=random.choice(users),
                question=random.choice(questions),
                content=fake.text(max_nb_chars=150)
            ))
            self.print_progress(i, num_answers, "ответов")
            if i % BATCH_SIZE == 0 or i == num_answers:
                Answer.objects.bulk_create(answer_objs)
                answer_objs = []
        answers = list(Answer.objects.all().order_by('id')[:num_answers])

        # Создание оценок
        self.stdout.write(f"Создаётся {num_ratings} оценок...")
        ql_objs = []
        al_objs = []
        for i in range(1, num_ratings + 1):
            is_positive = random.choice([True, False])
            user = random.choice(users)
            if random.choice([True, False]) and questions:
                ql_objs.append(QuestionLike(
                    user=user,
                    question=random.choice(questions),
                    is_positive=is_positive
                ))
            elif answers:
                al_objs.append(AnswerLike(
                    user=user,
                    answer=random.choice(answers),
                    is_positive=is_positive
                ))
            self.print_progress(i, num_ratings, "оценок")
            if i % BATCH_SIZE == 0 or i == num_ratings:
                QuestionLike.objects.bulk_create(ql_objs, ignore_conflicts=True)
                AnswerLike.objects.bulk_create(al_objs, ignore_conflicts=True)
                ql_objs = []
                al_objs = []

        self.stdout.write(self.style.SUCCESS("\nБаза данных заполнена тестовыми данными!"))