from .config import BatteryConf
from machine import Pin, SPI, ADC

class Battery:
    def measure():
        full_battery = BatteryConf.full_voltage
        empty_battery = BatteryConf.empty_voltage
        conversion_factor = 3 * 3.3 / 65535
        
        Pin(25, Pin.OUT, value=1)
        Pin(29, Pin.IN, pull=None)
        voltage = round(ADC(3).read_u16() * conversion_factor, 2)
        Pin(25, Pin.OUT, value=0, pull=Pin.PULL_DOWN)
        Pin(29, Pin.ALT, pull=Pin.PULL_DOWN, alt=7)
        
        percentage = 100 * ((voltage - empty_battery) / (full_battery - empty_battery))
        if percentage > 100:
            percentage = 100.00
        
        return percentage, voltage