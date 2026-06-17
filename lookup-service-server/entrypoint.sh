#!/bin/sh
fastapi run app/main.py --port 8000 &
FASTAPI_PID=$!

# Wait for server to be ready before starting schedule job
until curl -sf http://localhost:8000/docs > /dev/null 2>&1; do
  sleep 2
done

nohup python3 -u app/schedule_job.py \
  >> "${V1_LOG_DIR:-/var/log/perfsonar}/pslookup-backward-compatibility-agent-process.log" 2>&1 &

wait $FASTAPI_PID
