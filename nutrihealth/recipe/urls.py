"""
URLs that are related to recipes.
"""

from django.urls import path
from nutrihealth.recipe import views

urlpatterns = [
    path('', views.CuisineSearchView.as_view()),
    path('search/', views.RecipeSearchView.as_view()),
    path('add/', views.AddMealHistoryView.as_view()),
    path('remove_history/', views.RemoveMealHistoryView.as_view()),
    path('history/', views.WeeklyChartView.as_view()),
]