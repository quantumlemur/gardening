# Web server
`python3 testserver.py

# nodemcu files
- nodemcu/private contains files that aren't exposed to the autoupdater and must be manually copied.  This includes a credentials.lua file which should be created to store the wifi credentials
- nodemcu/exposed contains all the files which are exposed through the webserver and are subject to auto-updating on the device
