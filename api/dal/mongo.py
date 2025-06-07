from pymongo import MongoClient
from pymongo.collection import Collection
from api.config import get_settings

#client = MongoClient(os.getenv("MONGODB_URI", "mongodb+srv://sandeepk:sandeep@cluster0.tnbpi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"))
settings = get_settings()

# Example usage:
mongo_uri = settings.mongodb_uri
client = MongoClient(mongo_uri)
db = client["Raina"]

def get_collection(collection_name: str):
    def _get_collection() -> Collection:
        return db[collection_name]
    return _get_collection
