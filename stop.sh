#!/bin/sh

FILE="app.pid"

if [[ ! -f "$FILE" ]]; then
    echo "$FILE does not exist. Stopping not possible."
    exit 1
fi
kill $(cat $FILE)
rm $FILE