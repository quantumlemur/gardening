#!/bin/sh

. venv/bin/activate

export ESPIDF=/home/mike/gardening/firmware/esp-idf
export PATH=/home/mike/gardening/firmware/xtensa-esp32-elf/bin:$PATH

HASH=$(git rev-parse HEAD)
TAG=$(git describe --tags)

cd firmware/micropython/ports/esp32


echo "currentCommitHash = \"$HASH\"
currentCommitTag = \"$TAG\"" > modules/currentCommitHash.py


make

cp build-GENERIC_OTA/application.bin ../../../versions/$TAG.bin
    
