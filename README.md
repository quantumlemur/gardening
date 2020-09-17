# Web server
` source venv/bin/activate
` source environment
` flask run -h 192.168.86.33

# Initialize the db
` flask init-db

# nodemcu files
- nodemcu/private contains files that aren't exposed to the autoupdater and must be manually copied.
This includes a CREDENTIALS.lua file which should be created to store the wifi credentials
- nodemcu/exposed contains all the files which are exposed through the webserver and are subject to auto-updating on the device

# nodemcu setup
- Flash the firmware
- Upload CREDENTIALS.lua:
	`SSID = "ssid"
	`PASSWORD = "password"
- Upload fifo.lua
- Upload init.lua


# Serial console
` sudo chmod -R 777 /dev/ttyUSB0 ; stty -F /dev/ttyUSB0 115200 ; tail -f /dev/ttyUSB0