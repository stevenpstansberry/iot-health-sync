#!/bin/bash

# Load environment variables from the .env file in the directory above
source ../.env

# Load mock patients from a file
PATIENTS_FILE="mock_patients.txt"

# Define available devices
DEVICES=("device1" "device2" "device3" "device4" "device5")

# Calculate end time (current time + 30 minutes)
END_TIME=$((SECONDS + 1800))

# Generate and send encrypted telemetry data
while [[ $SECONDS -lt $END_TIME ]]; do
    # Pick a random device
    device=${DEVICES[$((RANDOM % ${#DEVICES[@]}))]}

    # Pick a random line from the file
    line=$(shuf -n 1 $PATIENTS_FILE)

    # Extract patient name and ID
    name=$(echo $line | cut -d ',' -f 1)
    patient_id=$(echo $line | cut -d ',' -f 2)

    # Generate normal telemetry data
    heart_rate=$((60 + RANDOM % 20))
    oxygen=$((90 + RANDOM % 10))
    temperature=$((36 + RANDOM % 2))

    # Occasionally send anomalous data (20% chance)
    if (( RANDOM % 100 < 20 )); then
        case $(( RANDOM % 3 )) in
            0)
                # High heart rate
                heart_rate=$((120 + RANDOM % 20))
                ;;
            1)
                # Low oxygen level
                oxygen=$((80 + RANDOM % 10))
                ;;
            2)
                # Fever
                temperature=$((39 + RANDOM % 2))
                ;;
        esac
    fi

    # Create JSON payload
    json_data=$(cat <<EOF
{
    "device_id": "$device",
    "patient_name": "$name",
    "patient_id": "$patient_id",
    "heart_rate": $heart_rate,
    "oxygen": $oxygen,
    "temperature": $temperature,
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "data_source": "iot_simulator",
    "message_id": "$(uuidgen)"
}
EOF
)

    # Encryption key from .env file
    encryption_key=$ENCRYPTION_KEY

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

echo "Telemetry generation completed after 30 minutes."