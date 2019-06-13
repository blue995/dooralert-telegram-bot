#!/bin/sh

source venv/bin/activate
if [[ $? -ne 0 ]];
    echo Sourcing did not work.
    exit $?
python -m dooralert &
echo $! > app.pid