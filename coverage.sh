#!/bin/sh

export LOG_DIR="tests/logs"

if [[ -d "$LOG_DIR" ]]; then
    rm -rf "$LOG_DIR"
fi

python -m unittest discover -s tests -p "test_*.py"
RET=$?
if [[ $RET -ne 0 ]]; then
    exit $RET
fi
pytest --cov dooralert/ --cov-report term --cov-report html
RET=$?
if [[ $RET -ne 0 ]]; then
    exit $RET
fi