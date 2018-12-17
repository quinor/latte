#!/usr/bin/bash
export MYPYPATH=$(pwd)"/venv/lib/python3.7/site-packages"
python3 -m mypy lattec
python3 -m flake8 lattec
