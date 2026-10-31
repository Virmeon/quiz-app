from django import forms
from django.contrib.auth.models import User
from .models import Category, Question, Answer, UserProfile, Rating

class UserRegisterForm(forms.ModelForm):
    email = forms.EmailField(required=False, label="Електронна пошта (необов'язково)")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Підтвердження пароля")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("password_confirm")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Паролі не збігаються!")
        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'image']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio']


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['stars']