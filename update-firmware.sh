#!/bin/sh
set -e

. venv/bin/activate

export ESPIDF=$(pwd)/firmware/esp-idf
export PATH=$(pwd)/firmware/xtensa-esp32-elf/bin:$PATH

HASH=$(git rev-parse HEAD)
TAG=$(git describe --tags)

cd firmware/micropython/ports/esp32


echo "currentVersionHash = \"$HASH\"
currentVersionTag = \"$TAG\"" > modules/currentVersionInfo.py


make

cp build-GENERIC_OTA/application.bin ../../../versions/$TAG.bin
    
