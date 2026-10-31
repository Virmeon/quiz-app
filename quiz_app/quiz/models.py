from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Профіль користувача
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Користувач")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватарка")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Про себе")

    def __str__(self):
        return f"Профіль: {self.user.username}"


class Category(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='categories', verbose_name="Автор")
    name = models.CharField(max_length=100, verbose_name="Назва категорії")
    description = models.TextField(blank=True, verbose_name="Опис")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Обкладинка категорії")
    favorites = models.ManyToManyField(User, related_name='favorite_categories', blank=True, verbose_name="Улюблені")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def is_verified(self):
        return self.author is None or self.author.is_superuser

    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(r.stars for r in ratings) / ratings.count(), 1)
        return 0.0

    def __str__(self):
        return self.name


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions', verbose_name="Категорія")
    text = models.TextField(verbose_name="Текст питання")
    image = models.ImageField(upload_to='questions/', blank=True, null=True, verbose_name="Зображення (необов'язково)")

    class Meta:
        verbose_name = "Питання"
        verbose_name_plural = "Питання"

    def __str__(self):
        return self.text[:50]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name="Питання")
    text = models.CharField(max_length=255, verbose_name="Текст відповіді")
    is_correct = models.BooleanField(default=False, verbose_name="Правильна відповідь")

    class Meta:
        verbose_name = "Відповідь"
        verbose_name_plural = "Відповіді"

    def __str__(self):
        return self.text


class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_results', verbose_name="Користувач")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категорія")
    score = models.IntegerField(verbose_name="Набрано балів")
    total_questions = models.IntegerField(verbose_name="Всього питань")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата проходження")

    class Meta:
        verbose_name = "Результат тесту"
        verbose_name_plural = "Результати тестів"

    def __str__(self):
        return f"{self.user.username} - {self.category.name}: {self.score}/{self.total_questions}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Користувач")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='ratings', verbose_name="Категорія")
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Оцінка (1-5)")

    class Meta:
        unique_together = ('user', 'category')
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинги"