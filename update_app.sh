#!/bin/bash
APP=$( dirname "${BASH_SOURCE[0]}" )
~/google_appengine/appcfg.py --oauth2 update_queues .
~/google_appengine/appcfg.py --oauth2 update app.yaml batch.yaml
~/google_appengine/appcfg.py --oauth2 update_cron .
#~/google_appengine/appcfg.py --oauth2 update_indexes .
