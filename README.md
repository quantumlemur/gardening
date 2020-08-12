# Web server
`source venv/bin/activate
`source env
`flask run -h 192.168.86.33

# Initialize the db
` flask init-db

# nodemcu files
- nodemcu/private contains files that aren't exposed to the autoupdater and must be manually copied.  This includes a credentials.lua file which should be created to store the wifi credentials
- nodemcu/exposed contains all the files which are exposed through the webserver and are subject to auto-updating on the device
