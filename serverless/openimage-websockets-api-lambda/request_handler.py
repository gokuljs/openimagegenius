import json
import logging
import os
from datetime import datetime, timezone
from uuid import UUID, uuid4

import boto3
import pydantic
import pydash as _

from openimage_backend_lib import database_models as models
from openimage_backend_lib import repository as repo_module
from pydantic import BaseModel, ValidationError, validator

dynamodb_client = boto3.client("dynamodb")
sqs_client = boto3.client("sqs")
sqs_queue_url = os.environ["SQS_REQUEST_URL"]
environment = repo_module.EnvironmentInfo()
repository = repo_module.Repository(dynamodb_client, environment)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Request(BaseModel):
    data: str
    request_type: str
    unique_user_id: str

    @validator('data')
    def max_length_256(cls, v):
        if len(v) > 256:
            raise ValueError("data exceeds the limit of 256 characters.")
        return v

    @validator('request_type')
    def request_type_validator(cls, v):
        if v.lower() not in models.REQUEST_TYPES:
            raise ValueError(f"Request type {v} is not recognized.")
        return v

    @validator('unique_user_id')
    def check_if_valid_uuid_v4(cls, v):
        UUID(v, version=4)
        return v


def request_handler(event, context):
    logger.info(event)
    try:
        json_body = json.loads(event["body"])
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": "mal-formed JSON"}
    try:
        request = Request(
            unique_user_id=_.get(
                event, "requestContext.authorizer.unique_user_id"),
            request_type=_.get(json_body, "request_type"),
            data=_.get(json_body, "data")
        )
    except ValidationError as excp:
        logger.info("Bad request")
        return {"statusCode": 400, "body": str(excp)}

    request_id = str(uuid4())
    maybe_existing_request = repository.get_request(request_id)
    if maybe_existing_request:
        logger.info("Conflict")
        return {"statusCode": 409, "body": "Request ID conflict, try again."}

    creation_time = datetime.now(tz=timezone.utc)
    creation_time_iso = creation_time.isoformat()
    creation_time_ts = creation_time.timestamp()

    new_request = models.RequestModel(
        requester_unique_user_id=request.unique_user_id,
        request_id=request_id,
        request_type=request.request_type,
        data=request.data,
        status="requested",
        creation_time_iso=creation_time_iso,
        creation_time_timestamp=creation_time_ts,
        update_time_iso=creation_time_iso,
        update_time_timestamp=creation_time_ts,
    )

    repository.save_new_request(new_request)

    sqs_client.send_message(
        QueueUrl=sqs_queue_url,
        MessageBody=json.dumps({
            "request_type": request.request_type,
            "data": request.data,
            "unique_request_id": request_id,
            "requester_unique_user_id": request.unique_user_id,
        }),
    )
    logger.info("Success")
    return {"statusCode": 200, "body": "Request Accepted."}