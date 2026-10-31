from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Category, Question, Answer, QuizResult, UserProfile, Rating
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm, 
    RatingForm, CategoryForm, QuestionForm
)

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, "Реєстрація успішна!")
            return redirect('quiz:category_list')
    else:
        form = UserRegisterForm()
    return render(request, 'quiz/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next') or 'quiz:category_list')
    else:
        form = AuthenticationForm()
    return render(request, 'quiz/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('quiz:category_list')


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Профіль оновлено!")
            return redirect('quiz:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    results = QuizResult.objects.filter(user=request.user).select_related('category').order_by('-created_at')

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'results': results,
        'profile': profile
    }
    return render(request, 'quiz/profile.html', context)


@login_required
def create_quiz(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.author = request.user
            category.save()
            messages.success(request, "Вікторину створено! Тепер додайте питання.")
            return redirect('quiz:add_question', category_id=category.id)
    else:
        form = CategoryForm()
    return render(request, 'quiz/create_quiz.html', {'form': form})


@login_required
def edit_quiz(request, category_id):
    category = get_object_or_404(Category, pk=category_id, author=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Вікторину успішно оновлено!")
            return redirect('quiz:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'quiz/edit_quiz.html', {'form': form, 'category': category})


@login_required
def delete_quiz(request, category_id):
    category = get_object_or_404(Category, pk=category_id, author=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Вікторину видалено!")
        return redirect('quiz:category_list')
    return render(request, 'quiz/delete_quiz_confirm.html', {'category': category})


@login_required
def toggle_favorite(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if category.favorites.filter(id=request.user.id).exists():
        category.favorites.remove(request.user)
        messages.info(request, "Видалено з улюблених.")
    else:
        category.favorites.add(request.user)
        messages.success(request, "Додано до улюблених!")
    return redirect(request.META.get('HTTP_REFERER') or 'quiz:category_list')


@login_required
def favorite_list(request):
    categories = request.user.favorite_categories.all()
    return render(request, 'quiz/favorite_list.html', {'categories': categories})


@login_required
def add_question(request, category_id):
    category = get_object_or_404(Category, pk=category_id, author=request.user)
    if request.method == 'POST':
        q_form = QuestionForm(request.POST, request.FILES)
        if q_form.is_valid():
            question = q_form.save(commit=False)
            question.category = category
            question.save()

            answers = request.POST.getlist('answers')
            correct_index = request.POST.get('correct_answer')

            for idx, ans_text in enumerate(answers):
                if ans_text.strip():
                    Answer.objects.create(
                        question=question,
                        text=ans_text,
                        is_correct=(str(idx) == str(correct_index))
                    )

            if 'add_more' in request.POST:
                return redirect('quiz:add_question', category_id=category.id)
            else:
                return redirect('quiz:category_list')
    else:
        q_form = QuestionForm()

    return render(request, 'quiz/add_question.html', {
        'q_form': q_form,
        'category': category,
        'question_count': category.questions.count()
    })


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'quiz/category_list.html', {'categories': categories})


@login_required
def quiz_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    questions = category.questions.prefetch_related('answers').all()

    if request.method == 'POST':
        score = 0
        total = questions.count()
        detailed_results = []

        for question in questions:
            selected_answer_id = request.POST.get(f'question_{question.id}')
            user_answer = None
            is_correct = False

            if selected_answer_id:
                user_answer = Answer.objects.filter(id=selected_answer_id, question=question).first()
                if user_answer and user_answer.is_correct:
                    score += 1
                    is_correct = True

            correct_answer = question.answers.filter(is_correct=True).first()

            detailed_results.append({
                'question': question,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct
            })

        QuizResult.objects.create(
            user=request.user,
            category=category,
            score=score,
            total_questions=total
        )

        user_rating = Rating.objects.filter(user=request.user, category=category).first()

        return render(request, 'quiz/quiz_result.html', {
            'category': category,
            'score': score,
            'total': total,
            'detailed_results': detailed_results,
            'user_rating': user_rating.stars if user_rating else None
        })

    return render(request, 'quiz/quiz_detail.html', {
        'category': category,
        'questions': questions
    })


@login_required
def rate_quiz(request, category_id):
    if request.method == 'POST':
        stars = request.POST.get('stars')
        category = get_object_or_404(Category, pk=category_id)
        if stars:
            Rating.objects.update_or_create(
                user=request.user,
                category=category,
                defaults={'stars': int(stars)}
            )
    return redirect('quiz:category_list')


@login_required
def user_results(request):
    results = QuizResult.objects.filter(user=request.user).select_related('category').order_by('-created_at')
    return render(request, 'quiz/user_results.html', {'results': results})