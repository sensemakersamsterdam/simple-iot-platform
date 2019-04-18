# Simple IoT platform

This repository shows how to deploy a simple IoT platform on a single virtual machine.



## EC2 and attached volume

https://eu-west-1.console.aws.amazon.com/ec2/v2/home?region=eu-west-1#Home:

```
chmod 400 sensemakers.pem
ssh -i sensemakers.pem ubuntu@ec2-18-202-35-226.eu-west-1.compute.amazonaws.com
```

Mount external EBS volume.

https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-using-volumes.html

```
/dev/sda1
/dev/sdb
```

```
lsblk
sudo file -s /dev/xvda1
sudo file -s /dev/xvdb
sudo mkfs -t ext4 /dev/xvdb
sudo mkdir /data
sudo mount /dev/xvdb /data
df

sudo file -s /dev/xvdb
ls -al /dev/disk/by-uuid/
```

```
UUID=220e1c58-b89f-4e03-a1f0-fa1567004554      /data   ext4    defaults,nofail        0       2
```

```
sudo cp /etc/fstab /etc/fstab.orig
vim /etc/fstab
sudo mount -a
```

Install git and clone the IoT data platform repository.

```
sudo apt-get install git
git clone https://github.com/sensemakersamsterdam/IoT-data-platform.git
```



## TTN and MQTT

https://console.thethingsnetwork.org/applications/sewerwatch

Install Anaconda.

```
cd /tmp
curl -O https://repo.anaconda.com/archive/Anaconda3-5.2.0-Linux-x86_64.sh
bash Anaconda3-5.2.0-Linux-x86_64.sh

source ~/.bashrc
conda update conda
conda update anaconda

pip install --upgrade pip
```

Install Mosquitto client.

```
sudo apt-get update
sudo apt-get install mosquitto-clients
```

```
mosquitto_sub -h eu.thethings.network -t '+/devices/+/events/activations' -u 'sewerwatch' -P ttn-account-v2.ACCESSKEY -v

mosquitto_sub -h eu.thethings.network -t '+/devices/+/up' -u 'sewerwatch' -P ttn-account-v2.ACCESSKEY -v
```

TTN is sending data in the following format.

```
{
  "app_id": "sewerwatch",
  "dev_id": "ratjeone",
  "hardware_serial": "0004A30B001FA5E5",
  "port": 1,
  "counter": 1807,
  "payload_raw": "AgD/AWQQDxJtjgEAEQBJADEAEM/yTgLI+Q==",
  "payload_fields": {
    "aquap_di": 63944,
    "bmp280_pr": 101997,
    "bmp280_te": 18,
    "board_ty": "Sensemakers Rig",
    "board_vo": 4196,
    "cond_co": 62159,
    "ds18b20_te": 16,
    "hcsr04_di": 49,
    "lora_port": 1,
    "lsm303agr_te": 15,
    "mb7092_di": 73,
    "sen0189_tb": 590,
    "version": 2,
    "vl53l0x_di": 17
  },
  "metadata": {
    "time": "2018-10-15T21:00:36.386255358Z",
    "frequency": 867.3,
    "modulation": "LORA",
    "data_rate": "SF12BW125",
    "airtime": 1974272000,
    "coding_rate": "4/5",
    "gateways": [
      {
        "gtw_id": "eui-0000024b080e0d5c",
        "timestamp": 3936617404,
        "time": "2018-10-15T21:00:36.347732Z",
        "channel": 4,
        "rssi": -113,
        "snr": 6.5,
        "rf_chain": 0,
        "latitude": 52.37414,
        "longitude": 4.91473,
        "altitude": 10
      },
      {
        "gtw_id": "eui-7276ff000b0300ae",
        "timestamp": 2190116636,
        "time": "2018-10-15T21:00:36.347734Z",
        "channel": 4,
        "rssi": -118,
        "snr": -13.2,
        "rf_chain": 0,
        "latitude": 52.35926,
        "longitude": 4.9085,
        "altitude": 42
      }
    ]
  }
}
```

Make sure the mounted external EBS volume is accessible.
Data and log files will be stored there.

```
sudo chmod 777 /data
```

Run the `mqtt_to_json.py` python script to subscribe to the MQTT topic and append the full JSON to a file.

```
pip install -r requirements.txt
mkdir /data/logs
cd /home/ubuntu && nohup python mqtt_to_json.py > /data/logs/mqtt_to_json.out 2>&1 &
```



## Jupyter

Choose a password for Jupyter and encode it.

`from notebook.auth import passwd; passwd()`

You will get the password in the following encoded form. This will be used in the Jupyter configuration file.

`sha1:ENCRYPTEDPASSWORD`

Create an SSL certificate.

```
sudo openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout sensemakers.key -out sensemakers.crt \
-subj "/C=NL/ST=Noord Holland/L=Amsterdam/O=Sensemakers/CN=David Salek/emailAddress=salekd@gmail.com"
```

Generate the jupyter configuration file

```
jupyter notebook --generate-config
vim .jupyter/jupyter_notebook_config.py
```

and make the following changes.

```
c.NotebookApp.certfile = '/home/ubuntu/sensemakers.crt'
c.NotebookApp.ip = '*'
c.NotebookApp.keyfile = '/home/ubuntu/sensemakers.key'
c.NotebookApp.open_browser = False
c.NotebookApp.password = 'sha1:ENCRYPTEDPASSWORD'
```

Make sure the `/data` directory is accessible by setting an environmental variable and run Jupyter from the `notebooks` directory.

```
export JUPYTER_PATH=/data
cd /home/ubuntu/python/notebooks && nohup jupyter notebook > /data/logs/jupyter.out 2>&1 &
```

In your security group, under inbound rules add custom TCP rule for port 8888.

https://ec2-18-202-35-226.eu-west-1.compute.amazonaws.com:8888/



## InfluxDB

Install InfluxDB.

```
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
source /etc/lsb-release
echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt-get update && sudo apt-get install influxdb
```

https://docs.influxdata.com/influxdb/v1.6/administration/authentication_and_authorization/

Make the following changes in `/etc/influxdb/influxdb.conf`

```
dir = "/data/influxdb/meta"
dir = "/data/influxdb/data"
wal-dir = "/data/influxdb/wal"
enabled = true
bind-address = ":8086"
auth-enabled = false
log-enabled = true
write-tracing = false
pprof-enabled = false
https-enabled = false
https-certificate = "/etc/ssl/influxdb.pem"
```

and create a new directory for data.

```
mkdir /data/influxdb
sudo chown influxdb:influxdb /data/influxdb
```

Start the service.

```
sudo service influxdb start
```

Run `influx` and create admin user.

```
CREATE USER admin WITH PASSWORD 'ADMINPASSWORD' WITH ALL PRIVILEGES
```

Create a database.

```
CREATE DATABASE sensemakers
```

Run the `mqtt_to_influx.py` python script to subscribe to the MQTT topic and write data to InfluxDB.

```
cd /home/ubuntu && nohup python mqtt_to_influx.py > /data/logs/mqtt_to_influx.out 2>&1 &
```

In your security group, under inbound rules add custom TCP rule for port 8086.
The database can be accessed externally in the following way.

```
influx -host ec2-18-202-35-226.eu-west-1.compute.amazonaws.com -port 8086 -username admin -password ADMINPASSWORD
```

```
SHOW DATABASES
USE sensemakers
SHOW MEASUREMENTS
SHOW SERIES
SHOW TAG KEYS
SHOW FIELD KEYS
```



## Grafana

Install Grafana.

http://docs.grafana.org/installation/debian/

```
wget https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana_5.3.0_amd64.deb 
sudo apt-get install -y adduser libfontconfig
sudo dpkg -i grafana_5.3.0_amd64.deb 
```

Make the following changes in `/etc/grafana/grafana.ini`

```
data = /data/grafana
protocol = http
http_port = 3000
type = sqlite3
host = 127.0.0.1:3306
name = grafana
user = root
path = grafana.db
admin_user = admin
admin_password = ADMINPASSWORD
enabled = true
```

and create a new directory for data.

```
mkdir /data/grafana
chown 777 /data/grafana
```

Start the service.

```
sudo service grafana-server start
```

In your security group, under inbound rules add custom TCP rule for port 3000.

http://ec2-18-202-35-226.eu-west-1.compute.amazonaws.com:3000/

Add datasource of type InfluxDB with url http://ec2-18-202-35-226.eu-west-1.compute.amazonaws.com:8086
Do not tick any authentication and specify the database, user and password in the InfluxDB Details section.

Create a new dashboard.
