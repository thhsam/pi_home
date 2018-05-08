#!/usr/bin.env python

__author__ = 'Tszho'

import bme680
import time
import httplib, urllib

key = 'Z9QT25MNCBU32D48'
sensor = bme680.BME680()

# These calibration data can safely be commented
# out, if desired.
print("Calibration data:")
for name in dir(sensor.calibration_data):

    if not name.startswith('_'):
        value = getattr(sensor.calibration_data, name)

        if isinstance(value, int):
            print("{}: {}".format(name, value))

# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

print("\n\nInitial reading:")
for name in dir(sensor.data):
    value = getattr(sensor.data, name)

    if not name.startswith('_'):
        print("{}: {}".format(name, value))

sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

# Up to 10 heater profiles can be configured, each
# with their own temperature and duration.
# sensor.set_gas_heater_profile(200, 150, nb_profile=1)
# sensor.select_gas_heater_profile(1)

print("\n\nPolling:")
try:
    while True:
        if sensor.get_sensor_data():
            output = "{0:.2f} C,{1:.2f} hPa,{2:.2f} %RH".format(sensor.data.temperature, sensor.data.pressure, sensor.data.humidity)

            if sensor.data.heat_stable:
                print("{0},{1} Ohms".format(output, sensor.data.gas_resistance))

            else:
                print(output)

            params = urllib.urlencode({'field1' : sensor.data.temoerature, 'field2' : sensor.data.pressure, 'field3' : sensor.data.humidity, 'key' : key})
            headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
            conn = httplib.HTTPConnection("api.thingspeak.com:80")

            try:
                conn.request("POST", "/update", params, headers)
                response = conn.getresponse()
                print response.status, response.reason
                #data = response.read()
                conn.close()
            except:
                print "connection failed"
            break
                
        time.sleep(10)

except KeyboardInterrupt:
    pass
