#!/bin/sh

. venv/bin/activate

export ESPIDF=/home/mike/gardening/firmware/esp-idf
export PATH=/home/mike/gardening/firmware/xtensa-esp32-elf/bin:$PATH

cd firmware/micropython/ports/esp32


echo "class CurrentCommitHash:
    currentCommitHash = \"$(git rev-parse HEAD)\"
    currentCommitTag = \"$(git describe --tags)\"" > modules/currentCommitHash.py


make

cp build-GENERIC_OTA/application.bin ../../../../api/static/
    
