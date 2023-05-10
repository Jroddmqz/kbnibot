from decouple import config
from pymongo import MongoClient


# Variables
URI = config("MONGO_URL", default=None)


class Mongo:
    def __init__(self, uri="", database="", collection="", data={} or []):
        self.data = data
        self.client = MongoClient(uri)
        self.db = self.client.get_database(database)
        self.collect = self.db.get_collection(collection)

    def find(self, document=None):
        if document is None:
            document = {}
        return list(self.collect.find(document))

    def find_one(self, document=None):
        if document is None:
            document = {}
        return self.collect.find_one(document)

    def insert_many(self, data=None):
        if data is None:
            data = []
        if isinstance(self.data, list):
            return self.collect.insert_many(self.data)
        else:
            try:
                return self.collect.insert_many(data)
            except TypeError:
                return "Envia una lista como parametro 'data'"

    def insert_one(self, data=None):
        if data is None:
            data = {}
        if isinstance(data, dict) and len(data) > 0:
            return self.collect.insert_one(data)
        elif isinstance(self.data, list):
            return "No tienes que pasar una lista"
        elif isinstance(data, list):
            return "No tienes que pasar una lista"
        elif isinstance(self.data, dict):
            return self.collect.insert_one(self.data)

    def update(self, old_data=None, new_data=None):
        if new_data is None:
            new_data = {}
        if old_data is None:
            old_data = {}
        return self.collect.update(old_data, {'$set': new_data})

    def update_one(self, old_data=None, new_data=None):
        if new_data is None:
            new_data = {}
        if old_data is None:
            old_data = {}
        return self.collect.update_one(old_data, {'$set': new_data})

    def delete_many(self, data=None):
        if data is None:
            data = {}
        return self.collect.delete_many(data)

    def delete_one(self, data=None):
        if data is None:
            data = {}
        return self.collect.delete_one(data)


async def confirm(user_db, data=None):
    if data is None:
        data = {}
    return user_db.find(data)


async def add_(user_db, data=None):
    if data is None:
        data = {}
    return user_db.insert_one(data)


async def update_(user_db, old_data=None, new_data=None):
    if old_data is None:
        old_data = {}
    if new_data is None:
        new_data = {}
    return user_db.update_one(old_data, new_data)


async def remove_(user_db, data=None):
    if data is None:
        data = {}
    return user_db.delete_one(data)


def confirm_ofdb(user_db, data=None):
    if data is None:
        data = {}
    return user_db.find(data)


def add_ofdb(user_db, data=None):
    if data is None:
        data = {}
    return user_db.insert_one(data)


def update_ofdb(user_db, old_data=None, new_data=None):
    if old_data is None:
        old_data = {}
    if new_data is None:
        new_data = {}
    return user_db.update_one(old_data, new_data)


def remove_ofdb(user_db, data=None):
    if data is None:
        data = {}
    return user_db.delete_one(data)


def remove_many(user_db, data=None):
    if data is None:
        data = {}
    return user_db.delete_many(data)