# Sensemakers IoT platform

## EC2 and attached volume

https://eu-west-1.console.aws.amazon.com/ec2/v2/home?region=eu-west-1#Home:

```
chmod 400 sensemakers.pem
ssh -i sensemakers.pem ubuntu@ec2-18-202-35-226.eu-west-1.compute.amazonaws.com
```

```
/dev/sda1
/dev/sdb
```

https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-using-volumes.html

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



## TTN

https://console.thethingsnetwork.org/applications/sewerwatch

```
cd /tmp
curl -O https://repo.anaconda.com/archive/Anaconda3-5.2.0-Linux-x86_64.sh
bash Anaconda3-5.2.0-Linux-x86_64.sh

source ~/.bashrc
conda update conda
conda update anaconda

pip install --upgrade pip
```

```
sudo apt-get update
sudo apt-get install mosquitto-clients
```

```
mosquitto_sub -h eu.thethings.network -t '+/devices/+/events/activations' -u 'sewerwatch' -P ttn-account-v2.ACCESSKEY -v

mosquitto_sub -h eu.thethings.network -t '+/devices/+/up' -u 'sewerwatch' -P ttn-account-v2.ACCESSKEY -v
```

```
pip install paho-mqtt
```

```
sudo chmod 777 /data
```

```
cd /home/ubuntu && nohup python mqtt_to_json.py > /home/ubuntu/mqtt_to_json.out 2>&1 &
```

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



## Jupyter

Generate new password

`from notebook.auth import passwd; passwd()`

`sha1:ENCRYPTEDPASSWORD`

```
sudo openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout sensemakers.key -out sensemakers.crt \
-subj "/C=NL/ST=Noord Holland/L=Amsterdam/O=Sensemakers/CN=David Salek/emailAddress=salekd@gmail.com"
```

```
jupyter notebook --generate-config
vim .jupyter/jupyter_notebook_config.py
```

```
c.NotebookApp.certfile = '/home/ubuntu/sensemakers.crt'
c.NotebookApp.ip = '*'
c.NotebookApp.keyfile = '/home/ubuntu/sensemakers.key'
c.NotebookApp.open_browser = False
c.NotebookApp.password = 'sha1:ENCRYPTEDPASSWORD'
```

```
mkdir notebooks
```

```
export JUPYTER_PATH=/data
cd /home/ubuntu/notebooks && nohup jupyter notebook > /home/ubuntu/jupyter.out 2>&1 &
```

In your security group, under inbound rules add custom TCP rule for port 8888.

https://ec2-18-202-35-226.eu-west-1.compute.amazonaws.com:8888/



## InfluxDB

```
curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
source /etc/lsb-release
echo "deb https://repos.influxdata.com/${DISTRIB_ID,,} ${DISTRIB_CODENAME} stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
sudo apt-get update && sudo apt-get install influxdb
```

https://docs.influxdata.com/influxdb/v1.6/administration/authentication_and_authorization/

`/etc/influxdb/influxdb.conf`

```
sudo service influxdb start
```

```
CREATE USER admin WITH PASSWORD '<password>' WITH ALL PRIVILEGES
```



## Grafana

http://docs.grafana.org/installation/debian/

```
wget https://s3-us-west-2.amazonaws.com/grafana-releases/release/grafana_5.3.0_amd64.deb 
sudo apt-get install -y adduser libfontconfig
sudo dpkg -i grafana_5.3.0_amd64.deb 
```

`/etc/grafana/grafana.ini`

```
sudo service grafana-server start
```
