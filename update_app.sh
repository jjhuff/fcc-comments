#!/bin/bash
APP=$( dirname "${BASH_SOURCE[0]}" )
appcfg.py --oauth2 update_queues .
appcfg.py --oauth2 update app.yaml batch.yaml
appcfg.py --oauth2 update_cron .
#appcfg.py --oauth2 update_indexes .
