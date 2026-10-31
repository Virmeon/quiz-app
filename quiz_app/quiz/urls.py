from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.quiz_detail, name='quiz_detail'),
    path('category/<int:category_id>/rate/', views.rate_quiz, name='rate_quiz'),
    path('category/<int:category_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('category/<int:category_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('category/<int:category_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_list, name='favorite_list'),
    path('my-results/', views.user_results, name='user_results'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('create-quiz/', views.create_quiz, name='create_quiz'),
    path('category/<int:category_id>/add-question/', views.add_question, name='add_question'),
]