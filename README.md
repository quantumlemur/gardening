# Development initial setup

## Computer side (frontend + backend)

### Dependencies
` sudo apt-get install python3

For LTS version of nodejs:
`curl -sL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
`sudo apt update; sudo apt install nodejs
Then for yarn:
`curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
`echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
`sudo apt-get update && sudo apt-get install yarn


### Create python venv
`python3 -m venv venv
`source venv/bin/activate
`pip install -r requirements.txt

### Init db (if needed; otherwise copy old db to instances/)
With venv still activated:
`flask init-db

### React setup
`yarn install


## Device side
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



# Development

## Computer development 
### Start development servers
` yarn start-api
` yarn start

API is accessible on localhost:5000
Frontend is accessible on localhost:3000

### Old flask web server
` source venv/bin/activate
` source environment
` flask run -h 192.168.86.33

### Initialize the db (only do this if needed)
` flask init-db



# Deployment

nginx reverse proxy on top, proxying to gunicorn for the api and nodejs for the frontend

`python3 -m venv venv
`source venv/bin/activate
`pip install -r requirements.txt
`deactivate
`yarn install
`yarn build

## Example systemd scripts
/etc/systemd/system/gunicorn.service:
```
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
Type=notify
# the specific user that our service will run as
User=gunicorn
Group=gunicorn
# another option for an even more restricted service is
# DynamicUser=yes
# see http://0pointer.net/blog/dynamic-users-with-systemd.html
RuntimeDirectory=gunicorn
WorkingDirectory=/var/lib/gardening
ExecStart=/var/lib/gardening/venv/bin/gunicorn --bind unix:/run/gunicorn.sock "api:create_app()"
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```


/etc/systemd/system/gunicorn.socket:
```
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock
# Our service won't need permissions for the socket, since it
# inherits the file descriptor by socket activation
# only the nginx daemon will need access to the socket
User=www-data
# Optionally restrict the socket permissions even more.
# Mode=600

[Install]
WantedBy=sockets.target
```

## Example nginx config
/etc/nginx/sites-enabled/gardening
```
server { 
  # if no Host match, close the connection to prevent host spoofing
  listen 80 default_server;
  return 444;
}

server { 
  # use 'listen 80 deferred;' for Linux
  # use 'listen 80 accept_filter=httpready;' for FreeBSD
  listen 80;
  client_max_body_size 4G;

  # set the correct host(s) for your site
  server_name nuc;

  keepalive_timeout 5;

  # path for static files
  root /var/lib/gardening/build;

  location / { 
    # checks for static file, if not found proxy to app
    try_files $uri /index.html;
  } 


  location /manage { 
    # checks for static file, if not found proxy to app
    try_files $uri @proxy_to_gunicorn;
  } 

  location /graph { 
    # checks for static file, if not found proxy to app
    try_files $uri @proxy_to_gunicorn;
  } 

  location /api { 
    # checks for static file, if not found proxy to app
    try_files $uri @proxy_to_gunicorn;
  } 

  location /device { 
    # checks for static file, if not found proxy to app
    try_files $uri @proxy_to_gunicorn;
  } 

  location @proxy_to_gunicorn { 
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Host $http_host;
    # we don't want nginx trying to do something clever with
    # redirects, we set the Host: header above already.
    proxy_redirect off;
    proxy_pass http://unix:/run/gunicorn.sock;
  } 

  error_page 500 502 503 504 /500.html;
  location = /500.html { 
    root /path/to/app/current/public;
  } 
}

```

## Enable services
`systemctl enable --now gunicorn.socket
`systemctl enable nginx.service

### Database init (if needed)
` flask init-db

### Api config
Create file instance/config.cfg, contents:
NODEMCU_FILE_PATH = "../nodemcu/exposed/"

# Tutorial sources
Setup was done by following the react+flask tutorial from
https://blog.miguelgrinberg.com/post/how-to-create-a-react--flask-project

nginx reverse proxy on top, proxying to gunicorn for the api and nodejs for the frontend
https://docs.gunicorn.org/en/stable/deploy.html?highlight=unix%20socket#monitoring
