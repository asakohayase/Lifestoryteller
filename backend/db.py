from typing import Any, Dict, List, Optional, TypedDict
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
import os


class MongoDBCollections(TypedDict):
    images: AsyncIOMotorCollection
    albums: AsyncIOMotorCollection


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    collections: Optional[MongoDBCollections] = None


async def connect_to_mongo():
    # if MongoDB.client is None:
    print(f"Connecting to MongoDB. Current client state: {MongoDB.client}")
    MongoDB.client = AsyncIOMotorClient(
        os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    )
    MongoDB.db = MongoDB.client.get_database("family_photo_album")
    MongoDB.collections = {
        "images": MongoDB.db.get_collection("images"),
        "albums": MongoDB.db.get_collection("albums"),
    }
    print(f"MongoDB connection established. New client state: {MongoDB.client}")


async def close_mongo_connection():
    print(f"Closing MongoDB. Current client state: {MongoDB.client}")
    client = MongoDB.client
    if client is not None:
        try:
            client.close()
            print("MongoDB connection closed")
        except Exception as e:
            print(f"Error closing MongoDB connection: {e}")
        finally:
            MongoDB.client = None
            MongoDB.db = None
            MongoDB.collections = None
    else:
        print("No active MongoDB connection to close")


def get_db() -> AsyncIOMotorDatabase:
    return MongoDB.db


def get_collection(name: str) -> AsyncIOMotorCollection:
    return MongoDB.collections[name]


async def save_image(file_path: str, metadata: Dict[str, Any]) -> str:
    images_collection = get_collection("images")
    result = await images_collection.insert_one(
        {"file_path": file_path, "metadata": metadata}
    )
    return str(result.inserted_id)


async def save_album(album_name: str, description: str, image_ids: List[str]) -> str:
    albums_collection = get_collection("albums")
    result = await albums_collection.insert_one(
        {"name": album_name, "description": description, "image_ids": image_ids}
    )
    return str(result.inserted_id)


async def get_recent_photos(limit: int = 10) -> List[Dict[str, Any]]:
    images_collection = get_collection("images")
    cursor = images_collection.find().sort("_id", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def get_albums() -> List[Dict[str, Any]]:
    albums_collection = get_collection("albums")
    cursor = albums_collection.find()
    return await cursor.to_list(length=None)
