from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import boto3
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../..', '.env'))

# S3 Configuration
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
)
S3_BUCKET_NAME = 'health-data-raw'

# Encryption configuration
encryption_key = bytes.fromhex("63663255767434797a59587252423657697151594131474749705a4766387644")  # 32 bytes (256-bit key)

def decrypt_data(encrypted_data):
    """Decrypt AES-256 encrypted data."""
    try:
        print(f"Starting decryption process...")
        encrypted_bytes = base64.b64decode(encrypted_data)
        iv = encrypted_bytes[:16]  # Extract IV (first 16 bytes)
        ciphertext = encrypted_bytes[16:]  

        cipher = AES.new(encryption_key, AES.MODE_CBC, iv)
        decrypted_bytes = unpad(cipher.decrypt(ciphertext), AES.block_size)
        print("Decryption successful")
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"Error during decryption: {e}")
        raise


def lambda_handler(event, context):
    try:
        print("Lambda function triggered")

        # Get the uploaded file details
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        print(f"Processing file from bucket '{bucket}' with key '{key}'")

        # Fetch the raw object from S3
        print("Fetching object from S3...")
        raw_object = s3_client.get_object(Bucket=bucket, Key=key)
        encrypted_data = raw_object['Body'].read().decode('utf-8')
        print("Encrypted data fetched successfully")

        # Decrypt the raw data
        decrypted_data = decrypt_data(encrypted_data)

        # Parse JSON and remove PII
        telemetry = json.loads(decrypted_data)
        print("Telemetry data parsed successfully")
        cleaned_data = {k: v for k, v in telemetry.items() if k not in ["patient_name", "patient_id"]}
        print("PII removed from telemetry data")

        # Save cleaned data to another S3 bucket
        cleaned_bucket = 'health-data-clean'
        cleaned_key = key.replace('raw_data/', 'cleaned_data/').replace('.enc', '.json')
        print(f"Uploading cleaned data to bucket '{cleaned_bucket}' with key '{cleaned_key}'")
        s3_client.put_object(
            Bucket=cleaned_bucket,
            Key=cleaned_key,
            Body=json.dumps(cleaned_data),
            ContentType='application/json'
        )
        print(f"Cleaned data saved successfully to '{cleaned_bucket}/{cleaned_key}'")

    except Exception as e:
        print(f"Error in lambda_handler: {e}")
        raise


if __name__ == "__main__":
    # Mock S3 event
    mock_event = {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": "health-data-raw"
                    },
                    "object": {
                        "key": "raw_data/sample.enc"
                    }
                }
            }
        ]
    }

    # Mock context 
    mock_context = {}

    # Call lambda_handler directly
    lambda_handler(mock_event, mock_context)
