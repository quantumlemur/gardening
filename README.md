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
git clone --recursive git@github.com:quantumlemur/gardening.git
cd gardening

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

flask init-db

yarn install
```

### Firmware development

Download the latest xtensa toolchain from https://docs.espressif.com/projects/esp-idf/en/latest/esp32s2/api-guides/tools/idf-tools.html
At the time of writing, the latest version was: https://dl.espressif.com/dl/xtensa-esp32-elf-gcc8_4_0-esp-2020r3-linux-amd64.tar.gz

```bash
cd firmware
wget https://dl.espressif.com/dl/xtensa-esp32-elf-gcc8_4_0-esp-2020r3-linux-amd64.tar.gz
tar -xzf xtensa-esp32-elf-gcc8_4_0-esp-2020r3-linux-amd64.tar.gz
```

Note: update-firmware.sh sets the xtensa path as an environment variable. You should set it manually (or add to \$PATH in .bashrc) if you'd like to manually build.

### Micropython build setup

Build cross-compiler support:

```bash
cd micropython
make -C mpy-cross
```

`git submodule update --init --recursive`

curl --header 'Authorization: token fec0ca29254694a0496317d96710a560f178c847' --header 'Accept: application/vnd.github.v3.raw' --remote-name --location https://api.github.com/repos/quantumlemur/gardening/contents/api/static/application.bin

## Device side

Build, erase, and do initial flash of the firmware

```bash
git tag 0
./update-firmware
cd firmware/micropython/ports/esp32/
make erase
make flash
```

# Development

## Computer development

### Start development servers

```bash
yarn start-api
yarn start
```

API is accessible on http://localhost:5000

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

# Tutorial sources

Setup was done by following the react+flask tutorial from
https://blog.miguelgrinberg.com/post/how-to-create-a-react--flask-project

nginx reverse proxy on top, proxying to gunicorn for the api and nodejs for the frontend
https://docs.gunicorn.org/en/stable/deploy.html?highlight=unix%20socket#monitoring

Micropython: https://github.com/micropython/micropython/wiki/Getting-Started
https://lemariva.com/blog/2019/08/micropython-vsc-ide-intellisense
https://lemariva.com/blog/2018/12/micropython-visual-studio-code-as-ide
https://blog.horan.hk/micropythonesp32.html

18:00 esp32 ] export ESPIDF=/home/mike/gardening/micropython/firmware/esp-idf
18:00 esp32 ] export PATH=/home/mike/gardening/micropython/firmware/xtensa-esp32-elf/bin:/home/mike/gardening/venv/bin:/home/mike/.local/bin:/home/mike/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/usr/lib/jvm/java-8-oracle/bin:/usr/lib/jvm/java-8-oracle/db/bin:/usr/lib/jvm/java-8-oracle/jre/bin:/home/mike/phone/android-sdk-linux/platform-tools
