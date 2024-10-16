from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, TypedDict
from urllib.parse import unquote
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


def generate_presigned_url(s3_object_name: str, expiration: int = 3600) -> str:
    """
    Generate a presigned URL for an S3 object.

    :param s3_object_name: The name of the object in S3
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string
    """
    try:
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": S3Config.get_bucket_name(),
                "Key": s3_object_name,
            },
            ExpiresIn=expiration,
        )
        return presigned_url
    except Exception as e:
        logger.error(
            f"Error generating presigned URL for object {s3_object_name}: {str(e)}"
        )
        raise


async def save_image(image_id: str, file_path: str, metadata: Dict[str, Any]) -> str:
    images_collection = get_collection("images")
    result = await images_collection.insert_one(
        {
            "_id": image_id,
            "file_path": file_path,
            "metadata": metadata,
            "created_at": datetime.now(timezone.utc),
        }
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
            "created_at": datetime.now(timezone.utc),
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
                presigned_url = generate_presigned_url(
                    image_doc["metadata"]["s3_object_name"]
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

async def get_albums() -> List[Dict[str, Any]]:
    try:
        albums_collection = get_collection("albums")
        cursor = albums_collection.find().sort("created_at", -1)
        albums = await cursor.to_list(length=None)

        formatted_albums = []
        for album in albums:
            formatted_album = {
                "id": str(album["_id"]),
                "album_name": album["album_name"],
                "description": album.get("description", ""),
                "images": [],
                "cover_image": None,
                "createdAt": (
                    album["created_at"].isoformat() if "created_at" in album else None
                ),
            }

            for image in album.get("images", []):
                if "id" in image and "url" in image:
                    presigned_url = generate_presigned_url(unquote(image["url"].split("/")[-1].split("?")[0]))
                    formatted_album["images"].append(
                        {"id": image["id"], "url": presigned_url}
                    )
            if formatted_album["images"]:
                formatted_album["cover_image"] = formatted_album["images"][0]

            formatted_albums.append(formatted_album)
        return formatted_albums
    except Exception as e:
        print(f"Error in get_albums: {str(e)}")
        raise


async def get_all_photos(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    try:
        images_collection = get_collection("images")
        cursor = images_collection.find().sort("created_at", -1).skip(skip).limit(limit)
        photos = await cursor.to_list(length=limit)
        return [
            {
                "id": str(photo["_id"]),
                "url": generate_presigned_url(photo["metadata"]["s3_object_name"]),
                "createdAt": (
                    photo["created_at"].isoformat() if "created_at" in photo else None
                ),
            }
            for photo in photos
        ]
    except Exception as e:
        logger.error(f"Error in get_all_photos: {str(e)}")
        raise

async def get_all_albums(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    try:
        albums_collection = get_collection("albums")
        cursor = albums_collection.find().sort("created_at", -1).skip(skip).limit(limit)
        albums = await cursor.to_list(length=limit)
        
        formatted_albums = []
        for album in albums:
            formatted_album = {
                "id": str(album["_id"]),
                "album_name": album["album_name"],
                "description": album.get("description", ""),
                "cover_image": None,
                "images": album.get("images", []),  
                "image_count": len(album.get("images", [])),
                "createdAt": (
                    album["created_at"].isoformat() if "created_at" in album else None
                ),
            }
            if album.get("images"):
                formatted_album["cover_image"] = {
                    "id": album["images"][0]["id"],
                    "url": generate_presigned_url(unquote(album["images"][0]["url"].split("/")[-1].split("?")[0]))
                }
            formatted_albums.append(formatted_album)
        print(f"Formatted {len(formatted_albums)} albums")
        return formatted_albums
    except Exception as e:
        print(f"Error in get_all_albums: {str(e)}")
        raise

async def get_recent_photos(limit: int = 4) -> List[Dict[str, Any]]:
    try:
        images_collection = get_collection("images")
        cursor = images_collection.find().sort("created_at", -1).limit(limit)
        photos = await cursor.to_list(length=limit)
        return [
            {
                "id": str(photo["_id"]),
                "url": generate_presigned_url(photo["metadata"]["s3_object_name"]),
                "createdAt": (
                    photo["created_at"].isoformat() if "created_at" in photo else None
                ),
            }
            for photo in photos
        ]
    except Exception as e:
        print(f"Error in get_recent_photos: {str(e)}")
        raise


async def get_recent_albums(limit: int = 4) -> List[Dict[str, Any]]:
    try:
        albums_collection = get_collection("albums")
        cursor = albums_collection.find().sort("created_at", -1).limit(limit)
        albums = await cursor.to_list(length=None)

        formatted_albums = []
        for album in albums:
            formatted_album = {
                "id": str(album["_id"]),
                "album_name": album["album_name"],
                "description": album.get("description", ""),
                "images": [],
                "cover_image": None,
                "createdAt": (
                    album["created_at"].isoformat() if "created_at" in album else None
                ),
            }

            for image in album.get("images", []):
                if "id" in image and "url" in image:
                    presigned_url = generate_presigned_url(unquote(image["url"].split("/")[-1].split("?")[0]))
                    formatted_album["images"].append(
                        {"id": image["id"], "url": presigned_url}
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


async def get_album_by_id(album_id: str):
    try:
        albums_collection = get_collection("albums")

        object_id = ObjectId(album_id)
        album = await albums_collection.find_one({"_id": object_id})

        if album is None:
            print(f"No album found with ID: {album_id}")
            return None

        formatted_album = {
            "id": str(album["_id"]),
            "album_name": album["album_name"],
            "description": album.get("description", ""),
            "images": [],
            "cover_image": None,
            "createdAt": (
                album["created_at"].isoformat() if "created_at" in album else None
            ),
        }

        for image in album.get("images", []):
            try:
                # Extract the full filename from the URL
                full_filename_encoded = image["url"].split("/")[-1].split("?")[0]
                # Decode the URL-encoded filename
                full_filename = unquote(full_filename_encoded)

                # Generate the presigned URL using the decoded filename
                presigned_url = generate_presigned_url(full_filename)

                # Append the presigned URL to the formatted album
                formatted_album["images"].append(
                    {"id": image["id"], "url": presigned_url}
                )
            except Exception as e:
                print(
                    f"Error generating presigned URL for image {image['id']}: {str(e)}"
                )

        # Set the cover image to the first image if available
        if formatted_album["images"]:
            formatted_album["cover_image"] = formatted_album["images"][0]
        return formatted_album

    except Exception as e:
        print(f"Error fetching album by ID {album_id}: {str(e)}")
        raise


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


async def delete_multiple_photos(image_ids: List[str]) -> Dict[str, Any]:
    """
    Delete multiple photos from the database and S3.

    :param image_ids: List of photo IDs to delete
    :return: Dictionary with successful and failed deletions
    """
    results = {"successful": [], "failed": []}
    images_collection = get_collection("images")
    albums_collection = get_collection("albums")
    print(f"Attempting to delete photos: {image_ids}")

    for image_id in image_ids:
        try:
            photo_doc = await images_collection.find_one({"_id": image_id})
            if not photo_doc:
                results["failed"].append(image_id)
                continue

            # Delete from S3
            s3_object_name = photo_doc["metadata"]["s3_object_name"]
            try:
                S3Config.client.delete_object(
                    Bucket=S3Config.get_bucket_name(),
                    Key=s3_object_name
                )
            except Exception as e:
                logger.error(f"Error deleting photo from S3: {str(e)}")
                results["failed"].append(image_id)
                continue

            # Delete from MongoDB
            delete_result = await images_collection.delete_one({"_id": image_id})
            if delete_result.deleted_count == 0:
                results["failed"].append(image_id)
                continue

            # Remove from albums
            await albums_collection.update_many(
                {"images.id": image_id},
                {"$pull": {"images": {"id": image_id}}}
            )

            results["successful"].append(image_id)
        except Exception as e:
            logger.error(f"Error deleting photo with ID {image_id}: {str(e)}")
            results["failed"].append(image_id)

    return results

async def delete_multiple_albums(album_ids: List[str]) -> Dict[str, Any]:
    """
    Delete multiple albums from the database.

    :param album_ids: List of album IDs to delete
    :return: Dictionary with successful and failed deletions
    """
    results = {"successful": [], "failed": []}
    albums_collection = get_collection("albums")

    for album_id in album_ids:
        try:
            print(f"Attempting to delete album with ID: {album_id}, Type: {type(album_id)}")
            object_id = ObjectId(album_id)
            delete_result = await albums_collection.delete_one({"_id": object_id})
            if delete_result.deleted_count == 0:
                results["failed"].append(album_id)
            else:
                results["successful"].append(album_id)
        except Exception as e:
            logger.error(f"Error deleting album with ID {album_id}: {str(e)}")
            results["failed"].append(album_id)

    return results



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
