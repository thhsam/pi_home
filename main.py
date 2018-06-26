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

# Set the humidity baseline to 40%, an optimal indoor humidity.
hum_baseline = 40.0

# This sets the balance between humidity and gas reading in the 
# calculation of air_quality_score (25:75, humidity:gas)
hum_weighting = 0.25

# Collect gas resistance burn-in values, then use the average
# of the last 50 values to set the upper limit for calculating
# gas_baseline.
print("Collecting gas resistance burn-in data for 5 mins\n")
while curr_time - start_time < burn_in_time:
     curr_time = time.time()
     if sensor.get_sensor_data() and sensor.data.heat_stable:
     gas = sensor.data.gas_resistance
     burn_in_data.append(gas)
     print("Gas: {0} Ohms".format(gas))
     time.sleep(1)

gas_baseline = sum(burn_in_data[-50:]) / 50.0


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
                gas = sensor.data.gas_resistance
                gas_offset = gas_baseline - gas

                hum = sensor.data.humidity
                hum_offset = hum - hum_baseline
                # Calculate hum_score as the distance from the hum_baseline.
                if hum_offset > 0:
                    hum_score = (100 - hum_baseline - hum_offset) / (100 - hum_baseline) * (hum_weighting * 100)

                else:
                    hum_score = (hum_baseline + hum_offset) / hum_baseline * (hum_weighting * 100)

                # Calculate gas_score as the distance from the gas_baseline.
                if gas_offset > 0:
                    gas_score = (gas / gas_baseline) * (100 - (hum_weighting * 100))

                else:
                    gas_score = 100 - (hum_weighting * 100)

                # Calculate air_quality_score. 
                air_quality_score = hum_score + gas_score
                print("{0},{1} Ohms, Air quality: {2:.2f}".format(output, sensor.data.gas_resistance, air_quality_score))

            else:
                print(output)

            params = urllib.urlencode({'field1' : sensor.data.temperature, 'field2' : sensor.data.pressure, 'field3' : sensor.data.humidity, 'key' : key})
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

        time.sleep(30)

except KeyboardInterrupt:
    pass
