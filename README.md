# Development initial setup

## Computer side (frontend + backend)

### Dependencies (python, nodejs, yarn)

```bash
sudo apt-get install python3 python3-dev python3-pip python3-venv python3-wheel

curl -sL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt update; sudo apt install nodejs

curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt-get update && sudo apt-get install yarn
```

### Download code, create python venv, initialize db, install yarn packages:

```bash
git clone git@github.com:quantumlemur/gardening.git
cd gardening

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

flask init-db

yarn install
```

## Device side

## nodemcu files

- nodemcu/private contains files that aren't exposed to the autoupdater and must be manually copied.
  This includes a CREDENTIALS.lua file which should be created to store the wifi credentials
- nodemcu/public contains all the files which are exposed through the webserver and are subject to auto-updating on the device

## nodemcu setup

1. Set your wifi network and server URL in `nodemcu/private/CREDENTIALS.lua`:

   ```lua
   SERVER_URL = "http://nuc/device"
   SSID = "ssid"
   PASSWORD = "password"
   ```

1. Flash the firmware, `nodemcu/nodemcu-master-19-modules-2020-08-12-00-38-52-integer.bin`
1. Upload `nodemcu/private/CREDENTIALS.lua`
1. Upload `nodemcu/private/fifo.lua`
1. Upload `nodemcu/private/init.lua`

## Serial console, if you have a device plugged in

`sudo chmod -R 777 /dev/ttyUSB0 ; stty -F /dev/ttyUSB0 115200 ; tail -f /dev/ttyUSB0`

# Development

## Computer development

### Start development servers

```bash
yarn start-api
yarn start
```

API is accessible on http://localhost:5000.

Frontend is accessible on http://localhost:3000

### Initialize the db (only do this if needed)

`flask init-db`

# Deployment

## Normal deployment steps

(note: is the gunicorn restart necessaary?)

```bash
git pull
yarn install
yarn build
sudo service gunicorn restart
```

## Deployment setup

**Overall:** nginx out in front, serving the built frontend files, and proxying to gunicorn for the backend

1. Install all dependencies (same as development), download code, install node and python packages, and build the code
1. Set up systemd service monitoring scripts for gunicorn
1. Configure nginx site
1. Start gunicorn and nginx services

### Dependencies, setup, and build

```bash
sudo apt install python3 nginx gunicorn

curl -sL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt update; sudo apt install nodejs

curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt-get update && sudo apt-get install yarn

git clone git@github.com:quantumlemur/gardening.git
cd gardening

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask init-db
deactivate

yarn install

yarn build
```

### Example systemd scripts

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

### Example nginx config

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

### Enable services

```bash
systemctl enable --now gunicorn.socket
systemctl enable nginx.service
```

# Micropython

```bash
sudo apt-get install build-essential libreadline-dev libffi-dev git pkg-config gcc-arm-none-eabi libnewlib-arm-none-eabi
cd micropython
git clone --recurse-submodules https://github.com/micropython/micropython.git
cd micropython/mpy-cross
make
cd ../ports/unix
make axtls
make
```

## Device

Flash device:

```bash
cd micropython
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-idf3-20200902-v1.13.bin
```

# Tutorial sources

Setup was done by following the react+flask tutorial from
https://blog.miguelgrinberg.com/post/how-to-create-a-react--flask-project

nginx reverse proxy on top, proxying to gunicorn for the api and nodejs for the frontend
https://docs.gunicorn.org/en/stable/deploy.html?highlight=unix%20socket#monitoring

Micropython: https://github.com/micropython/micropython/wiki/Getting-Started
https://lemariva.com/blog/2019/08/micropython-vsc-ide-intellisense
https://lemariva.com/blog/2018/12/micropython-visual-studio-code-as-ide
