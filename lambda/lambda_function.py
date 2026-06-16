import io
import logging
import urllib.parse
import boto3

from ETL.Extract import extract_data_from_string
from ETL.transform import transform

# Initialize logging and S3 client outside the handler for warm start benefits
logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3_client = boto3.client("s3")

def lambda_handler(event, context):
    try:
        # 1. Extract and safely decode bucket name and file key
        record = event["Records"][0]
        bucket_name = record["s3"]["bucket"]["name"]
        raw_object_key = record["s3"]["object"]["key"]
        
        # Safe URL decoding handles spaces (+) and special characters (%20)
        object_key = urllib.parse.unquote_plus(raw_object_key, encoding="utf-8")
        logger.info(f"Triggered by upload: s3://{bucket_name}/{object_key}")

        # 2. Download the CSV bytes from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_bytes = response["Body"].read()

        # 3. Extract data from the string stream
        csv_text = file_bytes.decode("utf-8")
        raw_data = extract_data_from_string(csv_text)
        logger.info(f"Extracted {len(raw_data)} data rows from {object_key}")

        # 4. Transform data using your shared pipeline module
        transformed_data = transform(raw_data)
        
        logger.info(
            f"Transform successful — "
            f"Branches: {len(transformed_data['branches'])}, "
            f"Transactions: {len(transformed_data['transactions'])}"
        )

        # (Database load steps for Redshift/Postgres will follow in subsequent tasks)
        return {
            "statusCode": 200,
            "body": f"Successfully processed {len(raw_data)} rows from {object_key}."
        }

    except Exception as e:
        logger.error(f"Error processing S3 event: {str(e)}", exc_info=True)
        raise e