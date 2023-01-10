"""
URLs that are related to exercise.
"""

from django.urls import path
from nutrihealth.exercise import views

urlpatterns = [
    path('', views.ExerciseHomeview.as_view()),
    path('add/', views.AddExerciseHistoryView.as_view()),
    path('recommendations/', views.RecommendExerciseView.as_view()),
    path('remove_history/', views.RemoveExerciseHistoryView.as_view()),
    path('search/', views.ExerciseSearchView.as_view()),
]