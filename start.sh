#!/bin/bash

cd /home/ubuntu/IoT-data-platform/python && nohup python mqtt_to_json.py > /data/logs/mqtt_to_json.out 2>&1 &

export JUPYTER_PATH=/data
cd /home/ubuntu/IoT-data-platform/notebooks && nohup jupyter notebook > /data/logs/jupyter.out 2>&1 &

sudo service influxdb start
sudo service grafana-server start
