"""
URLs that are related to recipes.
"""

from django.urls import path
from nutrihealth.login import views

urlpatterns = [
    path('', views.LoginUserView.as_view()),
    path('signup/', views.SignupView.as_view()),
    path('resetpwd/', views.ResetPwdView.as_view()),
    path('signup/newuser', views.NewUserView.as_view()),
    path('signup/proceed', views.ProceedView.as_view()),
]