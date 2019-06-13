#!/bin/sh

if [[ ! -f "app.pid" ]]; then
    echo "app.pid does not exist. Stopping not possible."
    exit 1
fi
kill $(cat app.pid)