from pymongo import MongoClient

# Connect to your Atlas deployment
uri = "mongodb+srv://wisdom:bp000063@cluster0.pxsne.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)


def createSearchIndex(dbName, collName, indexName):
    try:
        database = client.get_database(dbName)
        collection = database.get_collection(collName)

        # Define your Atlas Search index
        index = {
            "name": indexName,
            "definition": {
                "mappings": {
                    "dynamic": True,
                    "fields": {
                        "embedding": {
                            "dimensions": 1536,
                            "similarity": "cosine",
                            "type": "knnVector"
                        }
                    }
                }
            }
        }

        # Run the helper method
        result = collection.create_index(index)
        print(result)
    finally:
        client.close()
