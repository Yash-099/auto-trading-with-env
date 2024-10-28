#!/bin/bash

# Find all processes containing 'USOIL' or 'NIFTY'
processes=$(ps aux | grep -E 'USOIL|NIFTY' | grep -v grep)

# Check if any processes were found
if [ -z "$processes" ]; then
    echo "No USOIL or NIFTY processes found."
    exit 0
fi

# Print the processes that will be killed
echo "Found the following USOIL and NIFTY processes:"
echo "$processes"

# Extract the PIDs of the processes and kill them
echo "$processes" | awk '{print $2}' | xargs kill -9

echo "USOIL and NIFTY processes have been terminated."

./start_live_track.sh