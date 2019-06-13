#!/bin/sh

source venv/bin/activate
if [[ $? -ne 0 ]]; then
    echo Sourcing did not work.
    exit $?
fi
python -m dooralert &
echo $! > app.pid