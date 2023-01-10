import datetime

from bson import ObjectId
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic.base import TemplateView

from nutrihealth import db


class LoginUserView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'login.html', dict())

    def post(self, request, *args, **kwargs):
        # Create database connection
        database = db.default_database()
        collection = database.User

        # Check if email exists
        existing_users = collection.find({'email': request.POST.get("email")})
        if (existing_users.count()) != 1:
            return HttpResponse('<h1>Could not found user with given email.</h1>')

        matched_user = existing_users[0]
        if matched_user['password'] != request.POST.get("password"):
            return HttpResponse('<h1>Invalid password</h1>')

        request.session['logged_in_user'] = matched_user
        return HttpResponseRedirect('/dashboard')


class SignupView(TemplateView):
    template_name = "signup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class NewUserView(View):

    def post(self, request, *args, **kwargs):
        # Create database connection
        database = db.default_database()
        collection = database.User

        # Check if email already exists
        existing_users = collection.find({'email': request.POST.get("email")})
        if (existing_users.count()) > 0:
            return HttpResponse('<h1>Email already exist in the database.</h1>')

        # Insert User
        date_format = '%Y-%m-%d'
        today = datetime.datetime.today().strftime(date_format)
        user = dict()
        user['first_name'] = request.POST.get("first_name")
        user['last_name'] = request.POST.get("last_name")
        user['email'] = request.POST.get("email")
        user['password'] = request.POST.get("password")
        user['date_created'] = today
        user['date_modified'] = today
        user['daily_calories'] = "0"
        user['daily_water_intake'] = "0"
        user['height'] = "0"
        user['weight'] = "0"
        user['gender'] = ""
        collection.insert_one(user)

        # Login the user
        existing_users = collection.find({'email': request.POST.get("email")})
        matched_user = existing_users[0]
        request.session['logged_in_user'] = matched_user

        return HttpResponseRedirect('proceed')


class ProceedView(View):
    template_name = "proceed.html"

    def get(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        return render(request, self.template_name, dict())

    def post(self, request, *args, **kwargs):
        # Create database connection
        database = db.default_database()
        collection = database.User

        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        dob = request.POST.get("date_of_birth")
        gender = request.POST.get("gender")
        weight = request.POST.get("weight")
        height = request.POST.get("height")
        calories = request.POST.get("calories")
        water = request.POST.get("water")

        user = request.session['logged_in_user']
        date_format = '%Y-%m-%d'
        today = datetime.datetime.today().strftime(date_format)
        query = {'_id': user['_id']}
        new_values = {'$set': {
            'date_of_birth': dob,
            'gender': gender,
            'height': height,
            'weight': weight,
            'daily_calories': calories,
            'daily_water_intake': water,
            'date_modified': today,
        }}
        collection.update_one(query, new_values)

        # Login the user
        existing_users = collection.find({'_id': user['_id']})
        matched_user = existing_users[0]
        request.session['logged_in_user'] = matched_user

        return HttpResponseRedirect('/dashboard')



class ResetPwdView(View):

    def get(self, request, *args, **kwargs):
        # Create database connection
        database = db.default_database()
        collection = database.User

        # Check if email already exists
        existing_users = collection.find({'email': request.GET.get("email",'')})
        if (existing_users.count()) == 0:
            return JsonResponse({'message':'Account with entered email does not exist.'})
        if (existing_users.count()) > 1:
            return JsonResponse({'message': 'Internal Error: More than one account is associated with email.'})

        user = existing_users[0]
        send_mail('NutriHealth Password',
                  'Your password for Nutrihealth account is: ' + user['password'],
                  'tdarji@nyit.edu',
                  [user['email']],
                  fail_silently=False)

        return JsonResponse({'message':'Success. Check your email for the password.'})
