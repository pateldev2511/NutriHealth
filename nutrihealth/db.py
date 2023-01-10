"""
Utility to connect to the database.
"""

from pymongo import MongoClient


def default_database():
    client = MongoClient(
        'mongodb+srv://Parita:uQm3T!3dE!g5*!K@cluster0.y79rr.mongodb.net/NutriHelth?retryWrites=true&w=majority')
    db = client['NutriHelth']
    return db
