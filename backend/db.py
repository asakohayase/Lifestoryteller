import json
import logging
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
from bson import ObjectId
from qdrant_client import QdrantClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def object_id_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj


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
        MongoDB.client = AsyncIOMotorClient(
            os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        )
        MongoDB.db = MongoDB.client.get_database("family_photo_album")
        MongoDB.collections = {
            "images": MongoDB.db.get_collection("images"),
            "albums": MongoDB.db.get_collection("albums"),
        }


async def close_mongo_connection():
    client = MongoDB.client
    if client is not None:
        try:
            client.close()
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


async def save_image(image_id: str, file_path: str, metadata: Dict[str, Any]) -> str:
    images_collection = get_collection("images")
    result = await images_collection.insert_one(
        {"_id": image_id, "file_path": file_path, "metadata": metadata}
    )
    return str(result.inserted_id)


async def save_album(
    album_name: str, description: str, images: List[Dict[str, str]]
) -> str:
    albums_collection = get_collection("albums")
    result = await albums_collection.insert_one(
        {
            "album_name": album_name,
            "description": description,
            "images": images,
            "cover_image": images[0] if images else None,
        }
    )
    return str(result.inserted_id)


async def generate_album_with_presigned_urls(
    album_data: Dict[str, Any]
) -> Dict[str, Any]:
    images = []
    for image_id in album_data.get("image_ids", []):
        image_doc = await get_image_metadata(image_id)
        if not image_doc:
            print(f"No metadata found for image ID: {image_id}")
            continue
        if (
            image_doc
            and "metadata" in image_doc
            and "s3_object_name" in image_doc["metadata"]
        ):
            try:
                presigned_url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": S3Config.get_bucket_name(),
                        "Key": image_doc["metadata"]["s3_object_name"],
                    },
                    ExpiresIn=3600,
                )
                images.append({"id": str(image_id), "url": presigned_url})
            except Exception as e:
                print(f"Error generating presigned URL for image {image_id}: {str(e)}")

    if not images:
        raise ValueError("No valid images found for the album")

    album_id = await save_album(
        album_data["album_name"], album_data["description"], images
    )

    result = {
        "id": album_id,
        "album_name": album_data["album_name"],
        "description": album_data["description"],
        "images": images,
        "cover_image": images[0] if images else None,
    }

    return result


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

    try:
        albums_collection = get_collection("albums")
        cursor = albums_collection.find().sort("_id", -1)
        albums = await cursor.to_list(length=None)

        formatted_albums = []
        for album in albums:
            formatted_album = {
                "id": str(album["_id"]),
                "album_name": album["album_name"],
                "description": album.get("description", ""),
                "images": [],
                "cover_image": None,
            }

            for image in album.get("images", []):
                if "id" in image and "url" in image:
                    formatted_album["images"].append(
                        {"id": image["id"], "url": image["url"]}
                    )
            if formatted_album["images"]:
                formatted_album["cover_image"] = formatted_album["images"][0]

            formatted_albums.append(formatted_album)
        return formatted_albums
    except Exception as e:
        print(f"Error in get_albums: {str(e)}")
        raise


async def get_image_metadata(image_id: str):
    images_collection = get_collection("images")
    return await images_collection.find_one({"_id": image_id})


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
