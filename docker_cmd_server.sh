#!/bin/bash
git pull && gunicorn --bind 0.0.0.0:5000 server
