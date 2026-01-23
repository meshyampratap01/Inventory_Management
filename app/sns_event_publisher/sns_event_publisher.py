import json
import boto3
from botocore.utils import ClientError
from fastapi import status

from app.app_exception.app_exception import AppException
from app.dependencies import get_sns_topic_arn


class SNSEventPublisher:
    def __init__(
        self,
    ) -> None:
        self.client = boto3.client("sns", region_name="ap-south-1")
        self.topic_arn = get_sns_topic_arn()
        print(self.client)
        print("TOPIC ARN =", repr(self.topic_arn))

    def publish_event(self, payload: dict):
        try:
            self.client.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(payload),
                MessageAttributes={
                    "eventType": {"DataType": "String", "StringValue": "LOW_STOCK"},
                },
            )
        except ClientError as e:
            raise AppException(
                message="Failed to publish SNS event",
                error_code="SNS_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error": str(e)},
            )
