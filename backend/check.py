import json
from motor.motor_asyncio import AsyncIOMotorClient

from qdrant_client import QdrantClient


def check_qdrant_data(collection_name: str, limit: int = 2):
    client = QdrantClient("localhost", port=6333)

    try:
        collection_info = client.get_collection(collection_name)
        print(f"Collection info: {collection_info}")

        results = client.scroll(
            collection_name=collection_name,
            limit=limit,
            with_payload=True,
            with_vector=False,
        )

        print(f"\nFirst {limit} items in Qdrant collection '{collection_name}':")
        for point in results[0]:
            print(f"ID: {point.id}")
            print(f"Payload: {json.dumps(point.payload, indent=2)}")
            print("---")

    except Exception as e:
        print(f"Error checking Qdrant data: {str(e)}")


async def check_mongo_data(database_name: str, collection_name: str, limit: int = 2):
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client[database_name]
    collection = db[collection_name]

    try:
        # Get collection info
        collection_info = await db.command("collstats", collection_name)
        print(f"Collection info: {collection_info}")

        # Retrieve some documents
        cursor = collection.find().limit(limit)

        print(f"\nFirst {limit} items in MongoDB collection '{collection_name}':")
        async for document in cursor:
            print(json.dumps(document, default=str, indent=2))
            print("---")

    except Exception as e:
        print(f"Error checking MongoDB data: {str(e)}")
    finally:
        client.close()


async def check_id_consistency(
    qdrant_collection: str, mongo_collection: str, limit: int = 5
):
    try:
        qdrant_client = QdrantClient("localhost", port=6333)
        collections = qdrant_client.get_collections()
        print(
            f"Available Qdrant collections: {[col.name for col in collections.collections]}"
        )

        if qdrant_collection not in [col.name for col in collections.collections]:
            return f"Qdrant collection '{qdrant_collection}' does not exist"

        collection_info = qdrant_client.get_collection(qdrant_collection)
        print(f"Qdrant collection '{qdrant_collection}' info: {collection_info}")

        # Try to get points count using different methods
        count_info = qdrant_client.count(qdrant_collection)
        print(f"Qdrant count info: {count_info}")

        # Attempt to retrieve points using scroll
        scroll_points = qdrant_client.scroll(
            collection_name=qdrant_collection,
            limit=limit,
            with_payload=True,
        )[0]
        print(f"Retrieved {len(scroll_points)} points from Qdrant using scroll")

        # Attempt to retrieve points using search
        search_points = qdrant_client.search(
            collection_name=qdrant_collection,
            query_vector=[0.0] * collection_info.config.params.vectors.size,
            limit=limit,
        )
        print(f"Retrieved {len(search_points)} points from Qdrant using search")

    except Exception as e:
        return f"Failed to get Qdrant info: {str(e)}"

    try:
        mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")
        await mongo_client.admin.command("ismaster")
        db = mongo_client["family_photo_album"]
        mongo_coll = db[mongo_collection]

        mongo_count = await mongo_coll.count_documents({})
        print(f"MongoDB collection '{mongo_collection}' document count: {mongo_count}")
    except Exception as e:
        return f"Failed to connect to MongoDB or get collection info: {str(e)}"

    results = []
    for point in scroll_points:
        qdrant_id = point.id
        try:
            mongo_doc = await mongo_coll.find_one({"_id": qdrant_id})
            if mongo_doc:
                results.append(f"ID {qdrant_id} exists in both Qdrant and MongoDB")
            else:
                results.append(f"ID {qdrant_id} exists in Qdrant but not in MongoDB")
        except Exception as e:
            results.append(f"Error checking ID {qdrant_id}: {str(e)}")

    print("ID consistency check completed")
    return results
