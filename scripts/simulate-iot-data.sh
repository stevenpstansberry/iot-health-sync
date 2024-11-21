while true; do
    echo "{\"device_id\": \"device1\", \"heart_rate\": $((60 + RANDOM % 20)), \"oxygen\": $((90 + RANDOM % 10)), \"temperature\": $((36 + RANDOM % 2))}" \
        | nc localhost 9999
    sleep 1
done
