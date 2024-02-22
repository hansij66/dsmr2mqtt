# DSMR MQTT
MQTT client for Belgian and Dutch Smart Meter (DSMR) - "Slimme Meter". Written in Python 3.x

Connect Smart Meter via a P1 USB cable to e.g. Raspberry Pi.

Application will continuously read DSMR meter and parse telegrams.
Parsed telegrams are send to MQTT broker.

Includes Home Assistant MQTT Auto Discovery.

In `dsmr50.py`, specify:
* Which messages to be parsed
* MQTT topics and tags
* Auto discovery for Home Assistant

A typical MQTT message broadcast looks like:
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

A virtual DSMR parameter is implemented (el_consumed and el_returned, which is sum of tarif1 and tarif2 (night/low en day/normal tariff)) - as some have a dual tarif meter, while energy company administratively considers this as a mono tarif meter.

## Requirements
Install following python3 libraries
* paho-mqtt
* pyserial
* persist-queue

## Test the P1 adapter & USB connection:
Test if P1 adapter is functional and is providing dsmr data by running in a bash shell:
* `tail -f /dev/ttyUSB0`
* optionally first execute `sudo chmod o+rw /dev/ttyUSB0`
* Results should be similar to:
   ```
  tail -f /dev/ttyUSB0
  
  /Ene5\T210-D ESMR5.0

  1-3:0.2.8(50)
  0-0:1.0.0(240204171638W)
  0-0:96.1.1(xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
  1-0:1.8.1(024790.294*kWh)
  1-0:1.8.2(011140.310*kWh)
  1-0:2.8.1(010474.138*kWh)
  1-0:2.8.2(025578.620*kWh)
  .....
  .....
  ```

## Installation & Configuration
* Install Python3 packages per recommendation for your distro
* Install from github and configure:
  * mkdir & cd to your install location 
  * git clone https://github.com/hansij66/dsmr2mqtt.git
  * cd dsmr2mqtt/ 
* In `systemd/dsmr-mqtt.service`:
  * Adapt ExecStart under [Service] to ExecStart=/<your location>/dsmr-mqtt.py (default: `/opt/iot/dsmr`)
* sudo cp -p systemd/dsmr-mqtt.service /etc/systemd/system
* Copy `config.rename.py` to `config.py` and adapt for your configuration (minimal: mqtt ip, username, password)
  * Edit the MQTT configuration and know that the MQTT_TOPIC_PREFIX = "dsmr" will show these messages as topic dsmr/. Configuration will be shown as homeassistant/sensor/dsmr/

* `sudo systemctl enable dsmr-mqtt`
* `sudo systemctl start dsmr-mqtt`
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
Use
* http://mqtt-explorer.com/
to test &  inspect MQTT messages

A `test/dsmr.raw` simulation file is provided.
Set `PRODUCTION = False` in `config.py` to use the simulation file. No P1/serial connection is required.

Tested under Debian/Raspbian.
Tested with DSMR v5.0 meter in Netherlands and Belgium. For other DSMR versions, `dsmr50.py` needs to be adapted.
For all SMR specs, see [netbeheer](https://www.netbeheernederland.nl/dossiers/slimme-meter-15/documenten)
For Belgium/Fluvius, open your P1 port through [Fluvius portal](https://mijn.fluvius.be/): 

For encrypted P1/dsmr, there is a [fork](https://github.com/wehrmannit/dsmr2mqtt) available.

## Licence
GPL v3

## Versions
4.0.0
* Simplified design
* Patches from javl
* Some Patches from smartathome

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
