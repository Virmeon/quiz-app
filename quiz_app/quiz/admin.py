from django.contrib import admin
from .models import Category, Question, Answer, QuizResult

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ['text', 'category']
    list_filter = ['category']

    class Media:
        js = ('quiz/js/paste_image.js',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

    class Media:
        js = ('quiz/js/paste_image.js',)

admin.site.register(QuizResult)