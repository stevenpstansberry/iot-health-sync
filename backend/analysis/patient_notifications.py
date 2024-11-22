import redis_client
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

# Decryption utility 
encryption_key = bytes.fromhex("63663255767434797a59587252423657697151594131474749705a4766387644")  # 32 bytes (256-bit key)

def decrypt_patient_id(encrypted_id):
    cipher = AES.new(encryption_key, AES.MODE_ECB)
    encrypted_bytes = base64.b64decode(encrypted_id)
    decrypted_id = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
    return decrypted_id.decode('utf-8')

def patient_notifications(encrypted_patient_id):
    redis_conn = redis_client.get_redis_connection()
    key = f"anomalies:{encrypted_patient_id}"
    anomalies = redis_conn.hgetall(key)

    # Decrypt the patient ID for display
    decrypted_patient_id = decrypt_patient_id(encrypted_patient_id)

    print(f"Patient {decrypted_patient_id} Notification:")
    for anomaly, value in anomalies.items():
        try:
            anomaly_type, timestamp = anomaly.split(":", 1)  # Split at the first colon only
            print(f"  {anomaly_type} at {timestamp}: {value}")
        except ValueError:
            print(f"  Malformed anomaly key: {anomaly} -> {value}")

