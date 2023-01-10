
"""
URLs that are related to friends.
"""

from django.urls import path
from nutrihealth.friends import views

urlpatterns = [
    path('', views.FriendsListView.as_view()),
    path('add_friend/', views.AddFriendView.as_view()),
    path('search/', views.UserSearchView.as_view()),
    path('remove_friend/', views.RemoveFriendView.as_view()),
]