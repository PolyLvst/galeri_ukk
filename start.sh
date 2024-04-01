#!/bin/bash
VIRTUALENV=.data/venv/
if [ ! -d $VIRTUALENV ]; then
  python3 -m venv $VIRTUALENV
fi

if [ ! -f $VIRTUALENV/bin/pip ]; then
  curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | $VIRTUALENV/bin/python
fi

$VIRTUALENV/bin/pip install -r requirements-glitch.txt

$VIRTUALENV/bin/python3 storage_server.py
python3 storage_server.py