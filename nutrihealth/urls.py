"""nutrihealth URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from nutrihealth import views

import nutrihealth.views
from django.conf import settings

urlpatterns = [
    path('', views.HomeView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('about/', views.AboutView.as_view()),
    path('profile/', views.ProfileView.as_view()),
    path('user/<str:user_id>', views.UserView.as_view()),
    path('meal_planning/', views.MealPlanningView.as_view()),
    path('weight/add/', views.AddWeightView.as_view()),
    path('recommendations/', views.RecommendationView.as_view()),
    path('updateprofile/', views.UpdateProfile.as_view()),
    path('admin/', admin.site.urls),
    path('exercise/', include('nutrihealth.exercise.urls')),
    path('friends/', include('nutrihealth.friends.urls')),
    path('recipe/', include('nutrihealth.recipe.urls')),
    path('login/', include('nutrihealth.login.urls')),
    path('dashboard/', include('nutrihealth.dashboard.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
