#!/bin/bash

# Load environment variables from the .env file in the directory above
source ../.env

# Log file
LOG_FILE="telemetry_log_$(date +%Y%m%d%H%M%S).log"

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log "INFO" "Starting telemetry data generation."

# Load mock patients from a file
PATIENTS_FILE="mock_patients.txt"

if [ ! -f "$PATIENTS_FILE" ]; then
    log "ERROR" "Patients file '$PATIENTS_FILE' not found. Exiting."
    exit 1
fi

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
                log "WARNING" "Generated anomalous high heart rate: $heart_rate"
                ;;
            1)
                # Low oxygen level
                oxygen=$((80 + RANDOM % 10))
                log "WARNING" "Generated anomalous low oxygen level: $oxygen"
                ;;
            2)
                # Fever
                temperature=$((39 + RANDOM % 2))
                log "WARNING" "Generated anomalous high temperature: $temperature"
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

    log "INFO" "Generated JSON payload for device '$device': $json_data"

    # Encryption key from .env file
    encryption_key=$ENCRYPTION_KEY

    if [ -z "$encryption_key" ]; then
        log "ERROR" "Encryption key not found in environment variables. Exiting."
        exit 1
    fi

    # Generate a random IV (16 bytes in hex)
    iv=$(openssl rand -hex 16)

    # Encrypt the JSON payload with OpenSSL
    encrypted_data=$(printf '%s' "$json_data" | openssl enc -aes-256-cbc -a -K $encryption_key -iv $iv | tr -d '\n')

    if [ $? -ne 0 ]; then
        log "ERROR" "Failed to encrypt telemetry data for device '$device'. Skipping."
        continue
    fi

    # Combine IV and encrypted data
    combined_data="$iv:$encrypted_data"

    # Send the combined data to the server
    echo "$combined_data" | nc localhost 9999

    if [ $? -eq 0 ]; then
        log "INFO" "Successfully sent telemetry data for device '$device'."
    else
        log "ERROR" "Failed to send telemetry data for device '$device'."
    fi

    # Wait before sending the next message
    sleep 1
done

log "INFO" "Telemetry generation completed after 30 minutes."
