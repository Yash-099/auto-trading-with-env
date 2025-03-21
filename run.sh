#!/bin/bash

# Start both Python scripts in parallel
    python3 live_track/every_session.py --instrument NIFTY --upper 18000 18100 18200 --lower 17900 17800 17700 & 
PYTHONPATH=. python3 telegram_bot.py &

# Store the process IDs
pids=($!)

# Function to handle script termination
cleanup() {
    echo "Stopping all processes..."
    for pid in ${pids[@]}; do
        kill $pid 2>/dev/null
    done
    exit 0
}

# Set up trap for cleanup on script termination
trap cleanup SIGINT SIGTERM

# Wait for all background processes
wait
