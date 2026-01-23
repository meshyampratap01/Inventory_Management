import json
import os
import boto3

ses = boto3.client("ses", region_name="ap-south-1")

SENDER_EMAIL = os.environ["SENDER_EMAIL"]


def lambda_handler(event, context):
    for record in event["Records"]:
        sns_message = json.loads(record["Sns"]["Message"])

        if sns_message.get("event_type") != "LOW_STOCK":
            continue

        send_low_stock_email(sns_message)


def send_low_stock_email(data: dict):
    subject = f"🚨 Low Stock Alert – {data['product_name']}"

    body = f"""
    Hello,

    The following product has low stock:

    Product Name: {data["product_name"]}
    Product ID: {data["product_id"]}
    Category: {data["category"]}
    Current Quantity: {data["current_quantity"]}
    Threshold: {data["threshold"]}

    Please restock soon.

    — Inventory System
    """

    ses.send_email(
        Source=SENDER_EMAIL,
        Destination={"ToAddresses": [email for email in data["manager_email"]]},
        Message={"Subject": {"Data": subject}, "Body": {"Text": {"Data": body}}},
    )
