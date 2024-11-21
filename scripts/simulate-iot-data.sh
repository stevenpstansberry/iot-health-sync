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

    # Encryption key
    encryption_key="63663255767434797a59587252423657697151594131474749705a4766387644" 

    # Generate a random IV (16 bytes in hex)
    iv=$(openssl rand -hex 16)

    # Encrypt the JSON payload with OpenSSL
    encrypted_data=$(printf '%s' "$json_data" | openssl enc -aes-256-cbc -a -K $encryption_key -iv $iv | tr -d '\n')

    # Combine IV and encrypted data
    combined_data="$iv:$encrypted_data"

    # Send the combined data to the server
    echo "$combined_data" | nc localhost 9999

    # Wait before sending the next message
    sleep 1
done
