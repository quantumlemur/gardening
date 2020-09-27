# Initial setup

## Dependencies
` sudo apt-get install python3

For LTS version of nodejs:
`curl -sL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
`sudo apt update; sudo apt install nodejs
Then for yarn:
`curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
`echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
`sudo apt-get update && sudo apt-get install yarn





## Notes
Setup was done by following the react+flask tutorial from
https://blog.miguelgrinberg.com/post/how-to-create-a-react--flask-project

# Reach setup
` yarn install

# React app
` yarn start-api
` yarn start


# Old flask web server
` source venv/bin/activate
` source environment
` flask run -h 192.168.86.33

# Initialize the db (only do this if needed)
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


# Deployment

uwsgi on nginx
https://flask.palletsprojects.com/en/master/deploying/uwsgi/
