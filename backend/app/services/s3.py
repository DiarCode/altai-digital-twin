import boto3
from botocore.exceptions import NoCredentialsError
from app.core.config import settings

class S3Service:
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME
        
        # Prefer AWS_ vars, fallback to S3_ vars from .env
        access_key = settings.AWS_ACCESS_KEY_ID or settings.S3_ACCESS_KEY
        secret_key = settings.AWS_SECRET_ACCESS_KEY or settings.S3_SECRET_KEY
        region = settings.AWS_REGION or settings.S3_REGION
        endpoint = settings.S3_ENDPOINT

        self.s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            endpoint_url=endpoint
        )

    def upload_file(self, file_obj, object_name: str) -> str | None:
        """
        Upload a file to an S3 bucket
        :param file_obj: File to upload
        :param object_name: S3 object name
        :return: S3 path if file was uploaded, else None
        """
        try:
            self.s3.upload_fileobj(file_obj, self.bucket_name, object_name)
            return f"s3://{self.bucket_name}/{object_name}"
        except NoCredentialsError:
            print("Credentials not available")
            return None
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None

s3_service = S3Service()
