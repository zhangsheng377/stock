#!/bin/bash
git pull && gunicorn --bind 0.0.0.0:22222 func
