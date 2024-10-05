from typing import Any, Dict, List, Optional, TypedDict
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
import os
import boto3
from botocore.client import BaseClient
from botocore.config import Config
from qdrant_client import QdrantClient

s3_client = boto3.client(
    "s3", region_name=os.getenv("AWS_REGION"), config=Config(signature_version="s3v4")
)


class MongoDBCollections(TypedDict):
    images: AsyncIOMotorCollection
    albums: AsyncIOMotorCollection


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    collections: Optional[MongoDBCollections] = None


class S3Config:
    client: Optional[BaseClient] = None
    bucket_name: Optional[str] = None

    @classmethod
    def initialize(
        cls,
        bucket_name: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_region: Optional[str] = None,
    ):
        cls.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME")
        aws_access_key_id = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = aws_secret_access_key or os.getenv(
            "AWS_SECRET_ACCESS_KEY"
        )
        aws_region = aws_region or os.getenv("AWS_REGION")

        cls.client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region,
        )

    @classmethod
    def get_bucket_name(cls) -> str:
        if cls.bucket_name is None:
            raise ValueError(
                "S3 bucket name is not set. Please set it manually or through environment variables."
            )
        return cls.bucket_name


# Initialize S3 configuration
S3Config.initialize()


async def connect_to_mongo():
    if MongoDB.client is None:
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
        {"name": album_name, "description": description, "image_ids": image_ids or []}
    )
    return str(result.inserted_id)


async def get_recent_photos(limit: int = 8) -> List[Dict[str, Any]]:
    try:
        images_collection = get_collection("images")
        cursor = images_collection.find().sort("_id", -1).limit(limit)
        photos = await cursor.to_list(length=limit)
        return [
            {
                "id": str(photo["_id"]),
                "url": s3_client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": S3Config.get_bucket_name(),
                        "Key": photo["metadata"]["s3_object_name"],
                    },
                    ExpiresIn=3600,
                ),
            }
            for photo in photos
        ]
    except Exception as e:
        print(f"Error in get_recent_photos: {str(e)}")
        raise


async def get_albums() -> List[Dict[str, Any]]:
    albums_collection = get_collection("albums")
    cursor = albums_collection.find()
    return await cursor.to_list(length=None)


def upload_file_to_s3(
    file_path: str, object_name: Optional[str] = None
) -> Optional[str]:
    if object_name is None:
        object_name = os.path.basename(file_path)
    try:
        S3Config.client.upload_file(file_path, S3Config.get_bucket_name(), object_name)
        return f"https://{S3Config.get_bucket_name()}.s3.amazonaws.com/{object_name}"
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None


def generate_presigned_url(object_name: str, expiration: int = 3600) -> Optional[str]:
    try:
        url = S3Config.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3Config.get_bucket_name(), "Key": object_name},
            ExpiresIn=expiration,
        )
        return url
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None


# async def clear_all_images():
#     db = get_db()
#     await db.images.delete_many({})
#     await db.albums.delete_many({})
#     print("All images and albums have been deleted from MongoDB")


# def clear_qdrant_collection(collection_name: str):
#     client = QdrantClient("localhost", port=6333)
#     client.delete_collection(collection_name)
#     print(f"Qdrant collection '{collection_name}' has been deleted")


# async def clear_all_data(qdrant_collection_name: str):
#     await clear_all_images()
#     clear_qdrant_collection(qdrant_collection_name)
#     print("All data has been cleared from both MongoDB and Qdrant")
