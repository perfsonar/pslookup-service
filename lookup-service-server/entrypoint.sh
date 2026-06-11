#!/bin/sh
nohup python3 app/schedule_job.py \
  >> /var/log/perfsonar/pslookup-backward-compatibility-agent-process.log 2>&1 &

exec fastapi run app/main.py --port 8000
