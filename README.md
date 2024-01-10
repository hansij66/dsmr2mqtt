# DSMR MQTT
MQTT client for Dutch Smart Meter (DSMR) - "Slimme Meter". Written in Python 3.x
 
Connect Smart Meter via a P1 USB cable to e.g. Raspberry Pi.

Application will continuously read DSMR meter and parse telegrams.
Parsed telegrams are send to MQTT broker.

Includes Home Assistant MQTT Auto Discovery.

In `dsmr50.py`, specify:
* Which messages to be parsed
* MQTT topics and tags
* MQTT broadcast frequency
* Auto discovery for Home Assistant

A typical MQTT message broadcasted
{"V1":226.0,"V2":232.0,"V3":229.0,"database":"dsmr","el_consumed":24488767.0,"el_returned":21190375.0,"p_consumed":1130.0,"p_generated":0.0,"serial":"33363137","timestamp":1642275125}

A virtual DSMR parameter is implemented (el_consumed and el_returned, which is sum of tarif1 and tarif2 (nacht/low en day/normal tariff)) - as some have a dual tarif meter, while energy company administratively considers this as a mono tarif meter.

## Preparation
Test if P1 adapter is functional and providing dsmr data by running in a bash shell:
* `tail -f /dev/ttyUSB0`

## Usage:
* Copy `systemd/dsmr-mqtt.service` to `/etc/systemd/system`
* Adapt path in `dsmr-mqtt.service` to your install location (default: `/opt/iot/dsmr`)
* Copy `config.rename.py` to `config.py` and adapt for your configuration (minimal: mqtt ip, username, password)
* `sudo systemctl enable dsmr-mqtt`
* `sudo systemctl start dsmr-mqtt`

Use
* http://mqtt-explorer.com/
to test &  inspect MQTT messages

A `test/dsmr.raw` simulation file is provided.
Set `PRODUCTION = False` in `config.py` to use the simulation file. No P1/serial connection is required.

## Requirements
Install following python3 libraries
* paho-mqtt
* pyserial

Tested under Linux; there is no reason why it does not work under Windows.
Tested with DSMR v5.0 meter. For other DSMR versions, `dsmr50.py` needs to be adapted.
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
