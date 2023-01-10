import json

from bson import ObjectId, json_util
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.generic.base import TemplateView, View

from nutrihealth import db


def format_user(user):
    nu = user
    nu['id'] = str(user['_id'])
    return nu


def get_user(user_id: str, database):
    collection = database.User
    users_found = collection.find({'_id': ObjectId(user_id)})
    if users_found.count() > 0:
        return format_user(users_found[0])
    return None


def get_friend_ids(user_id: str, database):
    collection = database.Friends
    found_friends = collection.find({'user_id': user_id})
    if found_friends.count() > 0:
        return found_friends[0]['friends']
    return []


def get_friends(user_id: str, database):
    friend_ids = get_friend_ids(user_id, database)
    print("Friend Ids", friend_ids)
    users = list()
    for friend_id in friend_ids:
        user = get_user(friend_id, database)
        if user:
            users.append(user)
    return users


def search_user(term: str, existing_friends):
    if not term:
        return []
    database = db.default_database()
    collection = database.User
    email_match = collection.find({'email': {'$regex': term, '$options': 'i'}})
    fn_match = collection.find({'first_name': {'$regex': term, '$options': 'i'}})
    ln_match = collection.find({'last_name': {'$regex': term, '$options': 'i'}})
    users = list()
    user_ids = set()

    # Need to exclude existing friend
    for friend in existing_friends:
        user_ids.add(friend['id'])

    for matches in [email_match, fn_match, ln_match]:
        for match in matches:
            user = format_user(match)
            if user['id'] not in user_ids:
                users.append(user)
                user_ids.add(user['id'])
    return users


def add_frined(user_id: str, friend_id: str, database):
    collection = database.Friends

    found_records = collection.find({'user_id': user_id})
    if found_records.count() == 0:
        # No record found. create a new one.
        record = dict()
        record['user_id'] = user_id
        record['friends'] = [friend_id]
        collection.insert_one(record)
    else:
        # Update the existing record
        record = found_records[0]
        friends = record['friends']
        if friend_id not in friends:
            friends.append(friend_id)
        query = {'_id': record['_id']}
        new_values = {'$set': {'friends': friends}}
        collection.update_one(query, new_values)


def remove_friend(user_id: str, friend_id: str, database):
    collection = database.Friends
    found_records = collection.find({'user_id': user_id})
    if found_records.count() != 1:
        return False
    record = found_records[0]
    friends = record['friends']
    if friend_id in friends:
        friends.remove(friend_id)
        query = {'_id': record['_id']}
        new_values = {'$set': {'friends': friends}}
        collection.update_one(query, new_values)
    return True


class FriendsListView(TemplateView):
    template_name = "friends-list.html"

    def dispatch(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        return super(FriendsListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.session['logged_in_user']
        user_id = str(user['_id'])
        # user_id = "61a01287770d7ac866be6a89"

        database = db.default_database()
        friends = get_friends(user_id, database)
        print("Friends", friends)
        search_term = self.request.GET.get('search_term', None)
        search_results = search_user(search_term, friends)
        print("Searched users", search_results)

        context['friends'] = friends
        context['search_results'] = search_results
        context['place_holder'] = search_term if search_term else "Search by email, first name or last name"
        return context


class RemoveFriendView(View):

    def dispatch(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        return super(RemoveFriendView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        user = self.request.session['logged_in_user']
        user_id = str(user['_id'])
        friend_id = request.GET.get('friend_id', None)
        if not friend_id:
            return HttpResponse('<h1>Friend id not found</h1>')

        database = db.default_database()
        # Friendship is bidirectional
        if not remove_friend(user_id, friend_id, database):
            return HttpResponse(
                "<h1> More than one record found for user {} {} </h1>".format(user['first_name'], user['last_name']))
        if not remove_friend(friend_id, user_id, database):
            return HttpResponse(
                "<h1> More than one record found for user {} {} </h1>".format(user['first_name'], user['last_name']))

        return HttpResponseRedirect('/friends')


class AddFriendView(View):

    def dispatch(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        return super(AddFriendView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        user = self.request.session['logged_in_user']
        user_id = str(user['_id'])
        friend_id = request.GET.get('friend_id', None)
        if not friend_id:
            return HttpResponse('<h1>Friend id not found</h1>')

        database = db.default_database()
        # Friendship is bidirectional
        add_frined(user_id, friend_id, database)
        add_frined(friend_id, user_id, database)

        return HttpResponseRedirect('/friends')


class UserSearchView(View):

    def dispatch(self, request, *args, **kwargs):
        if 'logged_in_user' not in self.request.session:
            return HttpResponseRedirect('/login')

        return super(UserSearchView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        email = request.GET.get('email', None)
        if not email:
            return HttpResponse('<h1>Email not found</h1>')

        database = db.default_database()
        collection = database.User
        found_users = collection.find({'email': email})
        if found_users.count() != 1:
            return HttpResponse("<h1>More than one user found under email: {}</h1>".format(email))
        return JsonResponse(json.loads(json_util.dumps(found_users[0])), safe=False)
