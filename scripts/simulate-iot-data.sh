# Load mock names from a file
NAMES_FILE="mock_names.txt"

# Generate and send encrypted telemetry data
while true; do
    # Pick a random name from the file
    name=$(shuf -n 1 $NAMES_FILE)

    # Generate a random patient ID
    patient_id=$((1000 + RANDOM % 9000))

    # Generate telemetry data
    heart_rate=$((60 + RANDOM % 20))
    oxygen=$((90 + RANDOM % 10))
    temperature=$((36 + RANDOM % 2))

    # Create JSON payload
    json_data=$(cat <<EOF
{
    "device_id": "device1",
    "patient_name": "$name",
    "patient_id": "$patient_id",
    "heart_rate": $heart_rate,
    "oxygen": $oxygen,
    "temperature": $temperature
}
EOF
)

    # Encrypt the JSON payload
    encryption_key="cF2Uvt4yzYXrRB6WiqQYA1GGIpZGf8vD" 
    encrypted_data=$(echo -n "$json_data" | openssl enc -aes-256-cbc -a -salt -pass pass:$encryption_key)

    # Send encrypted data to the server
    echo "$encrypted_data" | nc localhost 9999

    # Wait before sending the next message
    sleep 1
done
