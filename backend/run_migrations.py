import asyncio
import os
import boto3

from botocore.config import Config

from db import (
    S3Config,
    close_mongo_connection,
    connect_to_mongo,
    get_collection,
    get_image_metadata,
)

s3_client = boto3.client(
    "s3", region_name=os.getenv("AWS_REGION"), config=Config(signature_version="s3v4")
)


async def migrate_albums():
    albums_collection = get_collection("albums")
    cursor = albums_collection.find({})

    async for album in cursor:
        # Convert image_ids to the new images structure
        if "image_ids" in album and "images" not in album:
            images = []
            for image_id in album["image_ids"]:
                image_doc = await get_image_metadata(image_id)
                if (
                    image_doc
                    and "metadata" in image_doc
                    and "s3_object_name" in image_doc["metadata"]
                ):
                    presigned_url = s3_client.generate_presigned_url(
                        "get_object",
                        Params={
                            "Bucket": S3Config.get_bucket_name(),
                            "Key": image_doc["metadata"]["s3_object_name"],
                        },
                        ExpiresIn=3600,
                    )
                    images.append({"id": str(image_id), "url": presigned_url})

            # Update the album document
            await albums_collection.update_one(
                {"_id": album["_id"]},
                {
                    "$set": {
                        "images": images,
                        "cover_image": images[0] if images else None,
                    },
                    "$unset": {"image_ids": ""},
                },
            )

        # Ensure album_name is present (in case it was named differently before)
        if "name" in album and "album_name" not in album:
            await albums_collection.update_one(
                {"_id": album["_id"]},
                {"$set": {"album_name": album["name"]}, "$unset": {"name": ""}},
            )

    print("Album migration completed.")


async def run_migrations():
    await connect_to_mongo()

    print("Starting migrations...")
    await migrate_albums()
    # Add more migration function calls here as needed
    print("Migrations completed.")

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(run_migrations())
