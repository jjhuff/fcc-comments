#!/bin/bash
APP=$( dirname "${BASH_SOURCE[0]}" )

dev_appserver.py app.yaml batch.yaml $*
