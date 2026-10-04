from machine import Pin, SoftI2C
from i2c_lcd import I2cLcd

# Menggunakan pin baru: SDA di 26, SCL di 27
i2c = SoftI2C(scl=Pin(27), sda=Pin(26), freq=100000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

lcd.clear()
lcd.putstr("Pin 26 & 27 OK!")