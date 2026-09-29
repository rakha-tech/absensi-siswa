from mfrc522 import MFRC522
from machine import Pin, SPI
import time

# Pinout HSPI ESP32
# SCK  -> GPIO 18 | MOSI -> GPIO 23 | MISO -> GPIO 19
# SDA  -> GPIO 5  | RST  -> GPIO 22

# 1. Turunkan baudrate ke 1MHz (1000000) agar sinyal data lebih stabil & tahan noise
spi = SPI(2, baudrate=1000000, polarity=0, phase=0)

# 2. Hard Reset RC522 via Pin RST sebelum inisialisasi
rst_pin = Pin(22, Pin.OUT)
rst_pin.value(0)
time.sleep_ms(50)
rst_pin.value(1)
time.sleep_ms(50)

rfid = MFRC522(spi=spi, gpioCs=5, gpioRst=22)

print("Koneksi Siap! Tempelkan Kartu RFID...")

while True:
    status, tag_type = rfid.request(rfid.REQIDL)
    
    if status == rfid.OK:
        status, raw_uid = rfid.anticoll()
        if status == rfid.OK:
            # Format UID 4 byte ke Hex
            uid_str = "0x" + "".join([f"{x:02X}" for x in raw_uid[:4]])
            print(f"UID Terbaca: {uid_str}")
            time.sleep(1) # Delay pembacaan ulang
            
    time.sleep_ms(100)