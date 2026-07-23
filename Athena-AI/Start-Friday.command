#!/bin/zsh

cd "$(dirname "$0")"
exec "$(pwd)/venv/bin/python" app.py
