from pymongo import MongoClient
import pandas as pd


def get_database(CONNECTION_STRING, database_name):
    client = MongoClient(CONNECTION_STRING)
    return client[database_name]


def create_collection(collection_name, database):
    return database[collection_name]


def add_document(document, collection):
    if type(document).__name__ == 'list':
        collection.insert_many(document)
    else:
        collection.insert_one(document)


def get_all_documents(collection):
    return pd.DataFrame(collection.find())


def collection_to_csv(collection, path):
    df = get_all_documents(collection)
    df.to_csv(path)
