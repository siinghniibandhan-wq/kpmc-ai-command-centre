from functools import lru_cache

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from .config import get_settings


class MissingGeminiCredential(RuntimeError):
    pass


@lru_cache
def get_gemini_api_key() -> str:
    settings = get_settings()
    if settings.gemini_api_key:
        return settings.gemini_api_key

    try:
        client = boto3.client("ssm", region_name=settings.aws_region)
        response = client.get_parameter(
            Name=settings.gemini_parameter_name,
            WithDecryption=True,
        )
        value = response["Parameter"]["Value"].strip()
        if not value:
            raise MissingGeminiCredential("The configured Gemini parameter is empty.")
        return value
    except (BotoCoreError, ClientError, KeyError) as exc:
        raise MissingGeminiCredential(
            "Gemini credentials are unavailable. Configure GEMINI_API_KEY or grant "
            "the backend IAM role ssm:GetParameter access to the configured SecureString."
        ) from exc
