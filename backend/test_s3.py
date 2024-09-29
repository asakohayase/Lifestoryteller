import os

from dotenv import load_dotenv
from db import upload_file_to_s3, generate_presigned_url, S3Config

load_dotenv()


def test_s3():
    bucket_name = os.getenv("S3_BUCKET_NAME")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION")

    print(f"S3 Bucket Name from environment: {bucket_name}")
    print(
        f"AWS Access Key ID from environment: {'Set' if aws_access_key_id else 'Not Set'}"
    )
    print(
        f"AWS Secret Access Key from environment: {'Set' if aws_secret_access_key else 'Not Set'}"
    )
    print(f"AWS Region from environment: {aws_region}")

    # Initialize S3Config
    S3Config.initialize(
        bucket_name=bucket_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_region=aws_region,
    )

    # Create a test file
    with open("test_file.txt", "w") as f:
        f.write("This is a test file")

    # Test upload
    s3_url = upload_file_to_s3("test_file.txt", "test_upload.txt")
    print(f"Uploaded file to S3: {s3_url}")

    # Test presigned URL generation
    presigned_url = generate_presigned_url("test_upload.txt")
    print(f"Generated presigned URL: {presigned_url}")

    # Clean up
    os.remove("test_file.txt")


if __name__ == "__main__":
    test_s3()
