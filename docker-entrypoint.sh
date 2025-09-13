#!/bin/bash

set -e

if [ "$1" = "cron" ]; then
    echo "Setting up cron job..."

    POST_TIME=${POST_TIME:-"09:00"}
    TIMEZONE=${TIMEZONE:-"UTC"}

    echo "REDDIT_CLIENT_ID=$REDDIT_CLIENT_ID" > /app/.env
    echo "REDDIT_CLIENT_SECRET=$REDDIT_CLIENT_SECRET" >> /app/.env
    echo "REDDIT_USERNAME=$REDDIT_USERNAME" >> /app/.env
    echo "REDDIT_PASSWORD=$REDDIT_PASSWORD" >> /app/.env
    echo "REDDIT_USER_AGENT=$REDDIT_USER_AGENT" >> /app/.env
    echo "POST_TIME=$POST_TIME" >> /app/.env
    echo "TIMEZONE=$TIMEZONE" >> /app/.env
    echo "POST_DELAY_SECONDS=$POST_DELAY_SECONDS" >> /app/.env

    echo "TZ=$TIMEZONE" >> /etc/environment
    ln -snf /usr/share/zoneinfo/$TIMEZONE /etc/localtime && echo $TIMEZONE > /etc/timezone

    CRON_HOUR=$(echo $POST_TIME | cut -d':' -f1)
    CRON_MINUTE=$(echo $POST_TIME | cut -d':' -f2)

    echo "$CRON_MINUTE $CRON_HOUR * * * cd /app && python bot/main.py --run-once >> /app/logs/cron.log 2>&1" > /etc/cron.d/reddit-bot

    chmod 0644 /etc/cron.d/reddit-bot

    crontab /etc/cron.d/reddit-bot

    echo "Cron job scheduled for $POST_TIME ($TIMEZONE)"
    echo "Starting cron daemon..."

    service cron start

    tail -f /app/logs/cron.log

elif [ "$1" = "run-once" ]; then
    echo "Running bot once..."
    cd /app && python bot/main.py --run-once

elif [ "$1" = "schedule" ]; then
    echo "Running bot with internal scheduler..."
    cd /app && python bot/main.py

else
    exec "$@"
fi