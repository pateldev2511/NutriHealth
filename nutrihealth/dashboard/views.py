import datetime

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.generic.base import TemplateView, View

from nutrihealth import db
from nutrihealth.exercise.views import get_exercises_for_today
from nutrihealth.recipe.views import get_meals_for_today


def get_water_intake_for_today(user_id: str):
    date_format = '%Y-%m-%d'
    today = datetime.datetime.today().strftime(date_format)

    database  = db.default_database()
    collection = database.WaterIntakeHistory
    histories = collection.find({
        '$and': [
            {'date_created': {'$regex': today}},
            {'user_id': user_id},
        ]})
    if histories.count() > 1:
        print("More than one water entry found per day")
        for h in histories:
            print(h)
        return 0
    if histories.count() == 0:
        return 0
    return histories[0]['water_intake']


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def dispatch(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        return super(DashboardView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.session['logged_in_user']
        user_id = str(user['_id'])
        meals_for_today = get_meals_for_today(user_id)
        exercises_for_today = get_exercises_for_today(user_id)
        total_water = get_water_intake_for_today(user_id)

        today_calories = 0
        for recipe in meals_for_today:
            today_calories += recipe['calories']
        consumed_calories = round(today_calories / (int(user['daily_calories'])) * 100, 2)

        total_water_perc = round(int(total_water) / (int(user['daily_water_intake'])) * 100, 2)

        context['meals_for_today'] = meals_for_today
        context['exercises_for_today'] = exercises_for_today
        context['today_calories'] = today_calories
        context['consumed_calories'] = consumed_calories
        context['total_water'] = total_water
        context['total_water_perc'] = total_water_perc
        context['user_id'] = user_id
        context['user'] = user
        return context


class AddWaterIntake(View):

    def get(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return JsonResponse({'message': 'user is log out.'})

        user = self.request.session['logged_in_user']
        user_id = str(user['_id'])
        print(user_id)

        intake = request.GET.get('waterintake', None)
        if not intake:
            return HttpResponse('<h1>Water intake not found </h1>')

        database = db.default_database()
        collection = database.WaterIntakeHistory

        date_format = '%Y-%m-%d'
        today = datetime.datetime.today().strftime(date_format)

        if get_water_intake_for_today(user_id) == 0:
            # Insert the new record
            water_intake = dict()
            water_intake['user_id'] = user_id
            water_intake['date_created'] = today
            water_intake['water_intake'] = intake
            collection.insert_one(water_intake)
        else:
            # Update the record
            query = {'$and': [
                {'date_created': {'$regex': today}},
                {'user_id': user_id},
            ]}
            new_value = {'$set': {'water_intake': intake}}
            collection.update_one(query, new_value)

        return HttpResponseRedirect('/dashboard')
