from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import random
from app.models import Profile, Question, Answer, Tag


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your login here',
        }),
        label='Login'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password here',
        }),
        label='Password'
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Проверяем авторизацию пользователя
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError('Invalid username or password!')
            elif not user.is_active:
                raise ValidationError('Account is disabled!')
            
            # Сохраняем пользователя в cleaned_data для использования во view
            cleaned_data['user'] = user

        return cleaned_data


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
        }),
        label='Password'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
        }),
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your username',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name',
            }),
        }
        labels = {
            'username': 'Username',
            'email': 'Email',
            'first_name': 'First Name',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('User with this email already exists!')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                raise ValidationError('Passwords do not match!')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            # Profile создастся автоматически через UserManager
        return user


class ProfileEditForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control w-75',
            'placeholder': 'Enter your username',
        }),
        label='Login',
        max_length=150
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control w-75',
            'placeholder': 'Enter your email',
        }),
        label='Email'
    )

    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control w-100',
            }),
        }
        labels = {
            'avatar': 'Upload avatar',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.user and User.objects.filter(username=username).exclude(id=self.user.id).exists():
            raise ValidationError('User with this username already exists!')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.user and User.objects.filter(email=email).exclude(id=self.user.id).exists():
            raise ValidationError('User with this email already exists!')
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        
        # Обновляем данные пользователя
        if self.user:
            self.user.username = self.cleaned_data['username']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        
        if commit:
            profile.save()
        
        return profile


class QuestionForm(forms.ModelForm):
    tags_input = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags separated by commas (e.g. python, django, web)',
        }),
        label='Tags',
        help_text='Enter tags separated by commas',
        required=False
    )

    class Meta:
        model = Question
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter question title',
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your question content',
                'rows': 6,
            }),
        }
        labels = {
            'title': 'Title',
            'content': 'Question Content',
        }

    def save(self, commit=True, author=None):
        question = super().save(commit=False)
        
        if author:
            question.author = author
        
        if commit:
            question.save()

            tags_input = self.cleaned_data.get('tags_input', '')
            if tags_input:
                # Список доступных Bootstrap цветов
                bootstrap_colors = ["primary", "secondary", "success", "danger", "warning", "info", "light", "dark"]
                
                tag_names = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={
                            'color_class': random.choice(bootstrap_colors)
                        }
                    )
                    question.tags.add(tag)
        
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your answer',
                'rows': 4,
            }),
        }
        labels = {
            'content': 'Your Answer',
        }

    def save(self, commit=True, author=None, question=None):
        answer = super().save(commit=False)
        
        if author:
            answer.author = author
        
        if question:
            answer.question = question
        
        if commit:
            answer.save()
        
        return answer
    
