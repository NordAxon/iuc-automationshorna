# Caution: written almost entirely by Copilot (Sonnet 3.5)

set -e
declare -a PGIDS=()

cleanup() {
    echo "Initiating cleanup..."
    
    # Kill all process groups
    for pgid in "${PGIDS[@]}"; do
        if kill -0 -$pgid 2>/dev/null; then
            echo "Killing process group $pgid"
            kill -TERM -$pgid 2>/dev/null || kill -9 -$pgid 2>/dev/null
        fi
    done
    
    # Stop docker container
    if [ -d "broker" ]; then
        cd broker && docker compose -p mqtt5 down || true
    fi
    
    echo "Cleanup complete"
    exit 0
}

trap cleanup SIGINT SIGTERM SIGQUIT

echo "Starting MQTT broker..."
cd broker && docker compose -p mqtt5 up -d

sleep 5

echo "Starting Python scripts..."
cd ..
setsid uv run mqtt_publisher.py &
PGIDS+=($!)

setsid uv run mqtt_subscriber.py &
PGIDS+=($!)

setsid uv run ../../src/main.py &
PGIDS+=($!)

echo "All services started. Press Ctrl+C to stop everything."

wait
