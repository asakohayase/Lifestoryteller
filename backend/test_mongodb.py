import asyncio
import os
from bson import ObjectId
from db import (
    connect_to_mongo,
    close_mongo_connection,
    get_collection,
    save_image,
    save_album,
    get_recent_photos,
    get_albums,
)
from PIL import Image


async def test_mongodb_operations():
    await connect_to_mongo()

    try:
        # Create a test image
        test_image_path = "test_image.jpg"
        image = Image.new("RGB", (100, 100), color="red")
        image.save(test_image_path)

        # Get actual file size
        file_size = os.path.getsize(test_image_path)

        # Test saving an image
        image_metadata = {
            "filename": "test_image.jpg",
            "size": file_size,
            "format": "JPEG",
            "width": 100,
            "height": 100,
        }
        image_id = await save_image(test_image_path, image_metadata)
        print(f"Saved image with ID: {image_id}")

        # Test saving an album
        album_name = "Test Album"
        album_description = "This is a test album"
        album_image_ids = [image_id]
        album_id = await save_album(album_name, album_description, album_image_ids)
        print(f"Saved album with ID: {album_id}")

        # Test getting recent photos
        recent_photos = await get_recent_photos(limit=5)
        print(f"Recent photos: {recent_photos}")

        # Test getting all albums
        albums = await get_albums()
        print(f"All albums: {albums}")

        # Clean up
        images_collection = get_collection("images")
        albums_collection = get_collection("albums")
        await images_collection.delete_one({"_id": ObjectId(image_id)})
        await albums_collection.delete_one({"_id": ObjectId(album_id)})
        os.remove(test_image_path)

    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(test_mongodb_operations())
