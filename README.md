# DSMR MQTT
MQTT client for Belgian Fluvius smart energy meter (DSMR5 spec) - "Slimme Meter". Written in Python 3.x
 
Connect the smart meter via a P1 USB cable to e.g. Raspberry Pi

Application will continuously read DSMR meter and parse telegrams which are send to a MQTT broker

Includes Home Assistant MQTT Auto Discovery

**Supported data fields:**

| OBIS CODE	| MEANING |
| ---|---|
| 0-0:96.1.4	| ID	|
| 0-0:96.1.1	| Serial number of electricity meter (in ASCII hex)	|
| 0-0:1.0.0	| Timestamp of the telegram	|
| 1-0:1.8.1	| Rate 1 (day) – total consumption	|
| 1-0:1.8.2	| Rate 2 (night) – total consumption	|
| 1-0:2.8.1	| Rate 1 (day) – total production	|
| 1-0:2.8.2	| Rate 2 (night) – total production	|
| 0-0:96.14.0	| Current rate (1=day,2=night)	|
| 1-0:1.7.0	| All phases consumption	|
| 1-0:2.7.0	| All phases production	|
| 1-0:21.7.0	| L1 consumption	|
| 1-0:41.7.0	| L2 consumption	|
| 1-0:61.7.0	| L3 consumption	|
| 1-0:22.7.0	| L1 production	|
| 1-0:42.7.0	| L2 production	|
| 1-0:62.7.0	| L3 production	|
| 1-0:32.7.0	| L1 voltage	|
| 1-0:52.7.0	| L2 voltage	|
| 1-0:72.7.0	| L3 voltage	|
| 1-0:31.7.0	| L1 current	|
| 1-0:51.7.0	| L2 current	|
| 1-0:71.7.0	| L3 current	|
| 0-0:96.3.10	| Switch position electricity	|
| 0-0:17.0.0	| Max. allowed power/phase	|
| 1-0:31.4.0	| Max. allowed current/plase	|
| 0-0:96.13.0	| Message	|
| 0-1:24.1.0	| Other devices on bus	|
| 0-1:96.1.1	| Serial number of natural gas meter (in ASCII hex)	|
| 0-1:24.4.0	| Switch position natural gas	|
| 0-1:24.2.3	| Reading from natural gas meter (timestamp) (value)	|

In `dsmr50.py`, specify:
* Which messages to be parsed
* MQTT topics and tags
* MQTT broadcast frequency
* Auto discovery for Home Assistant

A typical MQTT message broadcasted
```json
{
"V1":226.0,
"V2":232.0,
"V3":229.0,
"database":"dsmr",
"el_consumed":24488767.0,
"el_returned":21190375.0,
"p_consumed":1130.0,
"p_generated":0.0,
"serial":"33363137",
"timestamp":1642275125
}
```

A virtual DSMR parameter is implemented (el_consumed and el_returned, which is sum of tarif1 and tarif2 (nacht/low en dag/normal tariff)) - as some have a dual tariff meter, while energy company administratively considers this as a mono tarif meter.

```diff
-ATTENTION:
-Please open your P1 port through the Fluvius portal: https://mijn.fluvius.be/
-See Poortbeheer > Check that "Poort open"
```

## Requirements
* paho-mqtt
* pyserial
* python 3.x

## Test the USB connection before starting the scripts:
* Install packages and dependencies:
  * sudo apt-get install -y python3-paho-mqtt python3-serial python3-pip python3-crcmod python3-tabulatesudo
  * pip3 install paho-mqtt --usersudo
  * pip3 install persist-queue --user
  * sudo chmod o+rw /dev/ttyUSB0
* Test if you can read the P1 with your USB device:
  *  python3 -m serial.tools.miniterm /dev/ttyUSB0 115200 --xonxoff

* Results should be:
   ```python
    --- Miniterm on /dev/ttyUSB0  115200,8,N,1 ---
    --- Quit: Ctrl+] | Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H ---
    925*m3)
    !CE4E
    /FLU5\253xxxxxx_A

    0-0:96.1.4(xxxxx)
    0-0:96.1.1(xxxxxxxxxxxxxxxxxxxxxxxxxxxx)
    0-0:1.0.0(210204163628W)
    1-0:1.8.1(000439.094kWh)```

## Installation:
* Install Python packages:
  * sudo pip3 install paho-mqtt --user
  * sudo pip3 install persist-queue --user
* Install from Git and configure:
  * cd /opt
  * git clone https://github.com/smartathome/dsmr2mqtt.git
  * cd dsmr2mqtt/
  * sudo dos2unix systemd/dsmr-mqtt.service && sudo dos2unix config.rename.py
  * sudo vi systemd/dsmr-mqtt.service
* Adapt ExecStart under [Service] to ExecStart=/opt/dsmr2mqtt/dsmr-mqtt.py
  * sudo cp -p dsmr2mqtt/systemd/dsmr-mqtt.service /etc/systemd/system
* Edit the MQTT configuration and know that the MQTT_TOPIC_PREFIX = "dsmr" will show these messages as topic dsmr/. Configuration will be shown as homeassistant/sensor/dsmr/
  * sudo cp -p config.rename.py config.py && sudo vi config.py
  * sudo systemctl enable dsmr-mqtt
  * sudo systemctl start dsmr-mqtt
* And check if it is running properly
  * sudo systemctl status dsmr-mqtt
    ```python
    user@server:/opt/dsmr2mqtt $ sudo systemctl status dsmr-mqtt
    dsmr-mqtt.service - P1 dsmr smartmeter
     Loaded: loaded (/etc/systemd/system/dsmr-mqtt.service; enabled; vendor preset: enabled)
     Active: active (running) since Tue 2023-09-26 22:21:06 CEST; 18h ago
     Main PID: 1026 (dsmr-mqtt.py)
      Tasks: 6 (limit: 1595)
        CPU: 56.349s
     CGroup: /system.slice/dsmr-mqtt.service
             └─1026 /usr/bin/python3 /opt/dsmr2mqtt/dsmr-mqtt.py
             ```

Use http://mqtt-explorer.com/ to test & inspect MQTT messages or use the MQTT browser from within Home Assistant

A `test/dsmr.raw` simulation file is provided.
Set `PRODUCTION = False` in `config.py` to use the simulation file. In that case, no P1/serial connection is required.

Tested under Debian/Raspbian.
Tested with DSMR v5.0 meter in Belgium. For other DSMR versions, `dsmr50.py` needs to be adapted.
For all SMR specs, see [netbeheer](https://www.netbeheernederland.nl/dossiers/slimme-meter-15/documenten)

## Licence
GPL v3

## Versions
3.0.0
* Change HA Auto Discovery. Solve warning:
Discovered entities with a name that starts with the device name
This stops working in version 2024.2.0. Please address before upgrading.
Credits: ricko1

2.0.0 - 2.0.1
* Updated mqtt library
* Removed need for INFLUXDB label
* Added telegraf-dsmr.conf
* Added example (dsmr50_Stromnetz_Graz_Austria.py) for Austria dsmr (Stromnetz Graz, by karlkashofer)

1.0.13
* Add zero/non-zero check on data (as sometimes eg gas and power consumed values in influxdb became zero)

1.0.12
* Fix exit code (SUCCESS vs FAILURE)

1.0.2 - 1.0.4:
* Potential bug fix in parser
* Add MQTT last will/testament

1.0.0:
* Initial release
