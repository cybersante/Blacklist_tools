#!/bin/sh
gunicorn --chdir /app -b 0.0.0.0:8000 --timeout 1500 --workers 10 api:app
