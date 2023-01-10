import datetime
import json
import random
from typing import List

from bson import ObjectId, json_util
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.generic.base import TemplateView, View

from nutrihealth import db


def format_exercise(exercise):
    exer = exercise
    exer['id'] = str(exercise['_id'])
    return exer


def get_exercise(id: ObjectId, database):
    collection = database.Excercise
    exercises = collection.find({'_id': id})
    if exercises.count() > 0:
        return format_exercise(exercises[0])
    return None


def get_exercise_likes(user_id: str, database):
    collection = database.UserExcerciseLikes
    exercise_likes = collection.find({'user_id': user_id})
    if exercise_likes.count() > 0:
        return exercise_likes[0]['excercise']
    return []


def get_level_exercises(levels: List[str], database, limit=3):
    collection = database.Excercise
    random_number = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    exercises = collection.find({'level': {'$in': levels}}).limit(limit).skip(random_number)
    exers = list()
    for ex in exercises:
        exers.append(format_exercise(ex))
    return exers


def get_random_exercises(database, limit=10):
    collection = database.Excercise
    exercises = collection.aggregate([{'$sample': {'size': limit}}])
    exers = list()
    for ex in exercises:
        exers.append(format_exercise(ex))
    return exers


def get_exercises_for_today(user_id: str):
    date_format = '%Y-%m-%d'
    today = datetime.datetime.today().strftime(date_format)
    exercises = list()

    database = db.default_database()
    collection = database.ExcerciseHistory
    histories = collection.find({
        '$and': [
            {'date_created': {'$regex': today}},
            {'user_id': user_id},
        ]})
    for history in histories:
        exercise_id = ObjectId(history['excercise_id'])
        exercise = get_exercise(exercise_id, database)
        if exercise:
            exercise['duration'] = history['duration']
            exercise['exercise_history_id'] = str(history['_id'])
            exercises.append(exercise)
    print(exercises)
    return exercises


def get_recommendations(user_id: str, database):
    like_levels = get_exercise_likes(user_id, database)
    print(like_levels)

    recommendations = list()
    recommendations_id = set()
    for exercise in get_level_exercises(like_levels, database):
        recommendations.append(exercise)
        recommendations_id.add(exercise['_id'])
    remain = 5 - len(recommendations)  # Total 5 = 3 previous likes + 2 random
    for exercise in get_random_exercises(database):
        if exercise['_id'] not in recommendations_id and remain > 0:
            recommendations.append(exercise)
            recommendations_id.add(exercise['_id'])
            remain -= 1
    print("Exercise Recommendations ", recommendations)
    return recommendations


class ExerciseHomeview(TemplateView):
    template_name = "exercise_planning.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['placeholder_term'] = 'Search exercise database'
        return context


class ExerciseSearchView(TemplateView):
    template_name = "exercise_planning.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create database connection
        database = db.default_database()
        collection = database.Excercise

        # searched_term = kwargs['name']
        searched_term = self.request.GET.get('search_term', '')
        if not searched_term:
            return context

        matched_levels = collection.find({'level': {'$regex': searched_term, '$options': 'i'}})
        matched_names = collection.find({'name': {'$regex': searched_term, '$options': 'i'}})
        exercises = list()
        for level in matched_levels:
            exercises.append(format_exercise(level))
        for name in matched_names:
            exercises.append(format_exercise(name))

        context['placeholder_term'] = searched_term
        context['exercises'] = exercises
        context['matches'] = len(exercises)
        print("exercises", exercises)
        return context


class AddExerciseHistoryView(View):

    def get(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        user = self.request.session['logged_in_user']
        user_id = str(user['_id'])
        exercise_id = request.GET.get('exercise_id', None)
        duration = request.GET.get('duration', None)
        if not exercise_id or not duration:
            return HttpResponse('<h1>Exercise or duration not found</h1>')

        exercise = dict()
        exercise['user_id'] = user_id
        exercise['excercise_id'] = exercise_id
        exercise['duration'] = duration
        exercise['date_created'] = datetime.datetime.today().strftime('%Y-%m-%d')

        database = db.default_database()
        collection = database.ExcerciseHistory
        collection.insert_one(exercise)

        # Update user exercise likes here.
        exercise_obj = get_exercise(ObjectId(exercise_id), database)
        exercise_level = exercise_obj['level']
        like_levels = get_exercise_likes(user_id, database)
        if exercise_level not in like_levels:
            like_levels.append(exercise_level)
        exercise_like_collection = database.UserExcerciseLikes
        query = {'user_id': user_id}
        new_value = {'$set': {'excercise': like_levels}}
        exercise_like_collection.update_many(query, new_value)

        return HttpResponseRedirect('/dashboard')


class RemoveExerciseHistoryView(View):

    def get(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        user = self.request.session['logged_in_user']
        exercise_history_id = request.GET.get('exercise_history_id', None)
        if not exercise_history_id:
            return HttpResponse('<h1>Exercise history id not found</h1>')

        database = db.default_database()
        collection = database.ExcerciseHistory
        collection.delete_one({
            '$and': [
                {'_id': ObjectId(exercise_history_id)},
                {'user_id': str(user['_id'])}
            ]})
        return HttpResponseRedirect('/dashboard')


class RecommendExerciseView(View):

    def get(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        user = self.request.session['logged_in_user']
        user_id = str(user['_id'])
        # user_id = "61a01287770d7ac866be6a89"
        database = db.default_database()
        recommendations = get_recommendations(user_id, database)

        print(recommendations)
        return JsonResponse(json.loads(json_util.dumps(recommendations)), safe=False)
