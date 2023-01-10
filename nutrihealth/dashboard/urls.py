"""
URLs that are related to dashboard.
"""

from django.urls import path
from nutrihealth.dashboard import views

urlpatterns = [
    path('', views.DashboardView.as_view()),
    path('addwater/', views.AddWaterIntake.as_view()),
]