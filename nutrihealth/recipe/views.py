import ast
import collections
import json
import random
from datetime import datetime, timedelta
from typing import List

from bson import ObjectId
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.base import TemplateView, View

from nutrihealth import db


def format_recipe(recipe):
    frecipe = recipe
    frecipe['steps'] = ast.literal_eval(recipe['steps'])
    frecipe['tags'] = ast.literal_eval(recipe['tags'])
    nutrition = ast.literal_eval(recipe['nutrition'])
    frecipe['calories'] = nutrition[0]
    frecipe['fat'] = nutrition[1]
    frecipe['sugar'] = nutrition[2]
    frecipe['sodium'] = nutrition[3]
    frecipe['protein'] = nutrition[4]
    frecipe['id'] = str(recipe['_id'])
    return frecipe


def get_recipe(id: ObjectId, database):
    collection = database.Recipe
    recipes = collection.find({'_id': id})
    if recipes.count() > 0:
        return format_recipe(recipes[0])
    return None


def get_water_intake(date:str, user_id:str, database):
    collection = database.WaterIntakeHistory
    histories = collection.find({
        '$and': [
            {'date_created': {'$regex': date}},
            {'user_id': user_id},
        ]})
    if histories.count() > 1:
        print("More than one water entry found per day")
        for h in histories:
            print(h)
        return 0
    if histories.count() == 0:
        return 0
    return int(histories[0]['water_intake'])

def get_consumption(date: str, user_id: str):
    consumption = {
        'calories': 0,
        'fat': 0,
        'sodium': 0,
        'sugar': 0,
        'protein': 0,
        'water': 0,
    }
    database = db.default_database()
    collection = database.MealHistory

    histories = collection.find({
        '$and': [
            {'date_created': {'$regex': date}},
            {'user_id': user_id},
        ]})
    for history in histories:
        recipe_id = ObjectId(history['recipe_id'])
        recipe = get_recipe(recipe_id, database)
        if recipe:
            consumption['calories'] = consumption['calories'] + recipe['calories']
            consumption['sugar'] = consumption['sugar'] + recipe['sugar']
            consumption['protein'] = consumption['protein'] + recipe['protein']
            consumption['sodium'] = consumption['sodium'] + recipe['sodium']
            consumption['fat'] = consumption['fat'] + recipe['fat']
        print(history)

    consumption['water'] = get_water_intake(date, user_id, database)
    print(consumption)
    return consumption


def get_meals_for_today(user_id: str):
    date_format = '%Y-%m-%d'
    today = datetime.today().strftime(date_format)
    meals = list()

    database = db.default_database()
    collection = database.MealHistory
    histories = collection.find({
        '$and': [
            {'date_created': {'$regex': today}},
            {'user_id': user_id},
        ]})
    for history in histories:
        recipe_id = ObjectId(history['recipe_id'])
        recipe = get_recipe(recipe_id, database)
        recipe['meal_history_id'] = str(history['_id'])
        if recipe:
            meals.append(recipe)
    print(meals)
    return meals


def get_recipe_likes(user_id: str, database):
    collection = database.UserMealLikes
    recipe_likes = collection.find({'user_id': user_id})
    if recipe_likes.count() > 0:
        return recipe_likes[0]['meal_category']
    return []


def get_tag_recipes(tags: List[str], database, limit=3):
    collection = database.Recipe
    tag_str = " ".join(tags)
    random_number = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    recipes_found = collection.find({'$text': {'$search': tag_str}}).limit(limit).skip(random_number)
    recipes = list()
    for recipe in recipes_found:
        recipes.append(format_recipe(recipe))
    return recipes


def get_random_recipes(database, limit=6):
    collection = database.Recipe
    random_recipes = collection.aggregate([{'$sample': {'size': limit}}])
    recipes = list()
    for recipe in random_recipes:
        recipes.append(format_recipe(recipe))
    return recipes


def get_recommendations(user_id: str, database):
    # mealhistoryCollection = database.MealHistory
    # recipeCollection = database.Recipe
    #
    # # Get recipe and ids for user
    # consumed_recipe_ids = mealhistoryCollection.find({"user_id": user_id})
    # recipe_ids = list()
    # for user in consumed_recipe_ids:
    #     recipe_ids.append(user["recipe_id"])
    #
    # # getting unique recipes from user consumtions
    # distinct_recipe_ids = list(set(recipe_ids))
    #
    # recipe_ids_onjects = []
    # for id in distinct_recipe_ids:
    #     recipe_ids_onjects.append(ObjectId(id))
    #
    # # Get recipe tags
    # consumed_recipe_list = recipeCollection.find({"_id": {"$in": recipe_ids_onjects}})
    #
    # tag_dict = {}
    # tag_list = list()
    # for recipe in consumed_recipe_list:
    #     for tag in recipe["tags"][1:][:-1].replace("'", "").split(','):
    #         if tag not in tag_dict:
    #             tag_dict[tag] = 1
    #         else:
    #             tag_dict[tag] += 1
    #
    #         tag_list.append(tag)
    #
    # sorted_tag = sorted(tag_dict.items(), key=lambda kv: kv[1])
    # sorted_tag = sorted_tag[:-6][-20:]
    # sorted_tag = collections.OrderedDict(sorted_tag)
    #
    # # get the recommended recipe from tags of user consumed recipe
    # recommended_recipe = []
    # recipe_name = []
    # for each_tag in sorted_tag.keys():
    #     print(type(each_tag))
    #     matched_recipe = recipeCollection.find({'tags': {'$regex': each_tag.strip()}})
    #     for each in matched_recipe:
    #         print("in for :")
    #         print(each)
    #         if each['name'] not in recipe_name:
    #             print(each)
    #             recipe_name.append(each['name'])
    #             recommended_recipe.append(each)
    #             break
    #         else:
    #             break
    #
    #     if len(recipe_name) == 3:
    #         break

            # Format recipe and return context
    like_tags = get_recipe_likes(user_id, database)
    tag_recipes = get_tag_recipes(like_tags, database)

    recipes = []
    recipe_ids = set()
    for frecipe in tag_recipes:
        # frecipe = format_recipe(recipe)
        recipes.append(frecipe)
        recipe_ids.add(frecipe['id'])

    remain = 5 - len(recipes)
    random_recom = get_random_recipes(database)
    for frecipe in random_recom:
        if frecipe['id'] not in recipe_ids and remain > 0:
            recipes.append(frecipe)
            recipe_ids.add(frecipe['id'])
            remain -= 1

    return recipes


class RecipeHomeview(TemplateView):
    template_name = "recipe.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Recipe Search'
        context['info'] = 'Search recipe database'
        return context


class RecipeSearchView(TemplateView):
    template_name = "cuisine.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create database connection
        database = db.default_database()
        collection = database.Recipe

        # searched_term = kwargs['name']
        searched_term = self.request.GET.get('search_term', '')
        if not searched_term:
            return context

        # search_regex = ".*" + searched_term + ".*"
        matched_tags = collection.find({'tags': {'$regex': searched_term, '$options': 'i'}})
        matched_names = collection.find({'name': {'$regex': searched_term, '$options': 'i'}})
        recipes = list()
        for tag in matched_tags:
            recipes.append(format_recipe(tag))
        for name in matched_names:
            recipes.append(format_recipe(name))
        # print(recipes)

        context['placeholder_term'] = searched_term
        context['recipes'] = recipes
        context['matches'] = len(recipes)
        return context


class CuisineSearchView(TemplateView):
    template_name = "cuisine.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['placeholder_term'] = "breakfast"
        return context


class AddMealHistoryView(View):

    def get(self, request, *args, **kwargs):

        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        user = self.request.session['logged_in_user']
        user_id = str(user['_id'])
        recipe_id = request.GET.get('recipe_id', None)
        if not recipe_id:
            return HttpResponse('<h1>Recipe not found</h1>')

        meal = dict()
        meal['user_id'] = user_id
        meal['date_created'] = datetime.today().strftime('%Y-%m-%d')
        meal['recipe_id'] = recipe_id

        database = db.default_database()
        collection = database.MealHistory
        collection.insert_one(meal)

        # Update user meal likes here
        recipe = get_recipe(ObjectId(recipe_id), database)
        tags = recipe['tags']
        meal_likes = get_recipe_likes(user_id, database)
        new_likes = set()
        for like in meal_likes:
            new_likes.add(like)
        for tag in tags:
            new_likes.add(tag)
        query = {'user_id': user_id}
        new_value = {'$set': {'meal_category': list(new_likes)}}
        like_collection = database.UserMealLikes
        like_collection.update_many(query, new_value)

        return HttpResponseRedirect('/dashboard')


class RemoveMealHistoryView(View):

    def get(self, request, *args, **kwargs):

        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        user = self.request.session['logged_in_user']
        meal_history_id = request.GET.get('meal_history_id', None)
        if not meal_history_id:
            return HttpResponse('<h1>Meal history id not found</h1>')

        database = db.default_database()
        collection = database.MealHistory

        collection.delete_one({
            '$and': [
                {'_id': ObjectId(meal_history_id)},
                {'user_id': str(user['_id'])}
            ]})
        return HttpResponseRedirect('/dashboard')


class WeeklyChartView(TemplateView):
    template_name = 'chart.html'

    def dispatch(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        return super(WeeklyChartView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.session['logged_in_user']
        user_id = str(user['_id'])
        # user_id = "61a01287770d7ac866be6a89"

        # last 7 dates
        date_format = '%Y-%m-%d'
        dates = list()
        today = datetime.today()
        dates.append(today.strftime(date_format))
        cur = today
        for i in range(1, 7):
            cur = (cur - timedelta(days=1))
            dates.insert(0, cur.strftime(date_format))

        calories = list()
        sodium = list()
        sugar = list()
        fat = list()
        protein = list()
        water = list()

        print(dates)
        print(user_id)
        for date in dates:
            consumption = get_consumption(date, user_id)
            calories.append(consumption['calories'])
            sodium.append(consumption['sodium'])
            sugar.append(consumption['sugar'])
            fat.append(consumption['fat'])
            protein.append(consumption['protein'])
            water.append(consumption['water'])

        context['dates'] = json.dumps(dates)
        context['calories'] = calories
        context['sodium'] = sodium
        context['fat'] = fat
        context['sugar'] = sugar
        context['protein'] = protein
        context['water'] = water
        return context
