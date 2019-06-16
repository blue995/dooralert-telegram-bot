#!/bin/sh

python -m unittest discover -s tests -p "test_*.py"
RET=$?
if [[ $RET -ne 0 ]]; then
    exit $RET
fi
pytest --cov dooralert/ --cov-report term
RET=$?
if [[ $RET -ne 0 ]]; then
    exit $RET
fi