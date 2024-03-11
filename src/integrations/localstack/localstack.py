import os
from io import BytesIO

import aioboto3

from core.config import settings


class LocalStackS3:
    def __init__(self):
        self.__region_name = settings.localstack.REGION_NAME
        self.__url = settings.localstack.url
        self.__aws_access_key_id = settings.localstack.AWS_ACCESS_KEY_ID
        self.__aws_secret_access_key = settings.localstack.AWS_SECRET_ACCESS_KEY
        self.__bucket_name = settings.localstack.BUCKET_NAME

    def _create_s3_client(self):
        return aioboto3.Session().client(
            "s3",
            region_name=self.__region_name,
            endpoint_url=self.__url,
            aws_access_key_id=self.__aws_access_key_id,
            aws_secret_access_key=self.__aws_secret_access_key,
        )

    async def _create_bucket_if_not_exists(self):
        async with self._create_s3_client() as client:
            bucket_exists = False
            try:
                await client.head_bucket(Bucket=self.__bucket_name)
                bucket_exists = True
            except Exception as e:
                if "404" in str(e):
                    pass
                else:
                    raise e

            if not bucket_exists:
                await client.create_bucket(Bucket=self.__bucket_name)

    async def upload_image_to_localstack_and_get_path(self, image_file: bytes) -> str:
        await self._create_bucket_if_not_exists()
        object_name = f"images/{os.urandom(24).hex()}.jpg"

        async with self._create_s3_client() as client:
            await client.upload_fileobj(
                Fileobj=BytesIO(image_file),
                Bucket=self.__bucket_name,
                Key=object_name,
            )

        image_url = f"{self.__url}/{self.__bucket_name}/{object_name}"
        return image_url

    async def delete_image_from_localstack(self, image_path: str):
        object_name = image_path.split(f"{self.__url}/{self.__bucket_name}/")[-1]
        async with self._create_s3_client() as client:
            await client.delete_object(Bucket=self.__bucket_name, Key=object_name)


s3_client = LocalStackS3()
