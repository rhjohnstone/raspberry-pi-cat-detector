#!/bin/sh

export DISPLAY=:0
export DOORBELL="${HOME}/PycharmProjects/raspberry-pi-cat-doorbell-v2/raspberry-pi/doorbell.py"
nohup python3 "${DOORBELL}" > /tmp/doorbell.log 2>&1 &
