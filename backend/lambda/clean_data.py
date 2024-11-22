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
        print(f"Starting decryption. Encrypted data length: {len(encrypted_data)}")
        encrypted_bytes = base64.b64decode(encrypted_data)
        iv = encrypted_bytes[:16]  # Extract IV (first 16 bytes)
        ciphertext = encrypted_bytes[16:]  
        print(f"Extracted IV: {iv.hex()}")
        print(f"Ciphertext length: {len(ciphertext)}")

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
        print(f"Event data received: {json.dumps(event, indent=4)}")

        # Get the uploaded file details
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        print(f"File received: bucket={bucket}, key={key}")

        # Fetch the raw object from S3
        print(f"Fetching object from S3: bucket={bucket}, key={key}")
        raw_object = s3_client.get_object(Bucket=bucket, Key=key)
        encrypted_data = raw_object['Body'].read().decode('utf-8')
        print(f"Encrypted data fetched. Data length: {len(encrypted_data)}")

        # Decrypt the raw data
        decrypted_data = decrypt_data(encrypted_data)
        print(f"Decrypted data: {decrypted_data}")

        # Parse JSON and remove PII
        telemetry = json.loads(decrypted_data)
        print(f"Parsed telemetry data: {telemetry}")
        cleaned_data = {k: v for k, v in telemetry.items() if k not in ["patient_name", "patient_id"]}
        print(f"Cleaned telemetry data: {cleaned_data}")

        # Save cleaned data to another S3 bucket
        cleaned_bucket = 'health-data-clean'
        cleaned_key = key.replace('raw_data/', 'cleaned_data/').replace('.enc', '.json')
        print(f"Uploading cleaned data to S3: bucket={cleaned_bucket}, key={cleaned_key}")
        s3_client.put_object(
            Bucket=cleaned_bucket,
            Key=cleaned_key,
            Body=json.dumps(cleaned_data),
            ContentType='application/json'
        )
        print(f"Cleaned data saved to {cleaned_bucket}/{cleaned_key}")

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
                        "key": "raw_data/2024-11-22T01:49:53.944153_device1.enc"
                    }
                }
            }
        ]
    }

    # Mock context (can be an empty object if not used)
    mock_context = {}

    # Call lambda_handler directly
    lambda_handler(mock_event, mock_context)
