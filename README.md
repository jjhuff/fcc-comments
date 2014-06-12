fcc-comments
============

Quick and dirty AppEngine app to archive comments submitted for the FCC Net Neutrality rule making

0. Install the AppEngine SDK. Make sure `dev_appserver.py` is in your path. 
1. Run with `./run_dev.sh`
2. Load initial data with:
```
 curl "localhost:8081/import?zip=98122&proceeding=14-28"
```
3. Head to [http://localhost:8080] to see the result!
