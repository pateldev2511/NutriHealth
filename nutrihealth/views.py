import datetime
import ast
from bson.objectid import ObjectId
from django.views.generic.base import RedirectView, TemplateView, View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
import pymongo
from nutrihealth import db
from nutrihealth.friends.views import get_user, get_friend_ids
from nutrihealth.recipe.views import get_recommendations as recipe_recommendations
from nutrihealth.exercise.views import get_recommendations as exercise_recommendations


class LogoutView(RedirectView):
    url = '/'

    def get_redirect_url(self, *args, **kwargs):
        if 'logged_in_user' in self.request.session:
            self.request.session['logged_in_user'] = None
        return super().get_redirect_url(*args, **kwargs)


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ProfileView(TemplateView):
    template_name = "profile.html"

    def dispatch(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.session['logged_in_user']
        context['user'] = user
        return context


class UserView(TemplateView):
    template_name = 'user.html'

    def dispatch(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        return super(UserView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        database = db.default_database()
        #Current user
        user = self.request.session['logged_in_user']
        user_id = str(user['_id'])
        friend_ids = get_friend_ids(user_id, database)

        # Profile of the user
        profile_user_id = kwargs['user_id']
        profile = get_user(profile_user_id, database)

        # Check if they are friends
        is_friend = False
        if profile_user_id in friend_ids:
            is_friend = True

        context['user'] = profile
        context['is_friend'] = is_friend
        return context


class UpdateProfile(View):
    
    def get(self, request, *args, **kwargs):
        # Create database connection
        database = db.default_database()
        collection = database.User

        if 'logged_in_user' not in self.request.session:
             return JsonResponse({'message':'user is log out.'})

        user = self.request.session['logged_in_user']

        database = db.default_database()
        collection = database.User

        first_name = request.GET.get('first_name', None)
        last_name = request.GET.get('last_name', None)
        email = request.GET.get('email', None)
        password = request.GET.get('password', None)
        date_of_birth = request.GET.get('date_of_birth', None)
        gender = request.GET.get('gender', None)
        height = request.GET.get('height', None)
        weight= request.GET.get('weight', None)
        daily_calories = request.GET.get('daily_calories', None)
        daily_water_intake =  request.GET.get('daily_water_intake', None)

        date_format = '%Y-%m-%d'
        today = datetime.datetime.today().strftime(date_format)
        #dob = date_of_birth.strftime(date_format)
        query = {'_id': user['_id']}
        new_values = {"$set":
                        {
                            "first_name" :first_name,
                            "last_name" : last_name,
                            "email" : email,
                            "password" : password,
                            "date_of_birth" : date_of_birth,
                            "gender" :gender,
                            "height" :height,
                            "weight" :weight,
                            "daily_calories" :daily_calories,
                            "daily_water_intake" : daily_water_intake,
                            "date_modified" : today
                        }}
        collection.update_one(query, new_values)

        # Login the user
        existing_users = collection.find({'_id': user['_id']})
        matched_user = existing_users[0]
        request.session['logged_in_user'] = matched_user
        
        return JsonResponse({'message':'User Updated sucessfully.'})

class MealPlanningView(TemplateView):
    template_name = "meal_planning.html"

    def dispatch(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        return super(MealPlanningView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AddWeightView(View):

    def get(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        user = self.request.session['logged_in_user']
        weight = request.GET.get('weight', None)
        if not weight:
            return HttpResponse('<h1>Weight not found</h1>')

        history = dict()
        history['user_id'] = str(user['_id'])
        history['weight'] = str(weight)
        history['date_created'] = datetime.datetime.today().strftime('%Y-%m-%d')

        database = db.default_database()
        collection = database.WeightHistory
        collection.insert_one(history)
        return HttpResponseRedirect('/dashboard')


class RecommendationView(TemplateView):
    template_name = "recommendation.html"
    def dispatch(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        return super(RecommendationView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.session['logged_in_user']
        user_id = str(user['_id'])
        #user_id = "61a01287770d7ac866be6a89"
        database = db.default_database()

        context['recommended_recipe'] = recipe_recommendations(user_id, database)
        context['recommended_exercise'] = exercise_recommendations(user_id, database)
        return context