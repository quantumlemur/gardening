#!/bin/sh

. venv/bin/activate

export ESPIDF=/home/mike/gardening/micropython/firmware/esp-idf
export PATH=/home/mike/gardening/micropython/firmware/xtensa-esp32-elf/bin:$PATH

cd micropython/firmware/micropython/ports/esp32


echo "class CurrentCommitHash:
    currentCommitHash = \"$(git rev-parse HEAD)\"" > modules/currentCommitHash.py

make

cp build-GENERIC_OTA/application.bin ../../../../../api/static/
    
