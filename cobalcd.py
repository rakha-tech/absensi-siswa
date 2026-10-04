from machine import Pin, SPI, SoftI2C
from mfrc522 import MFRC522
from i2c_lcd import I2cLcd
import time

# Inisialisasi I2C LCD (SDA di 26, SCL di 27)
i2c = SoftI2C(scl=Pin(27), sda=Pin(26), freq=100000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

lcd.clear()
lcd.putstr("Sistem Siap!\nTempelkan Kartu")

# Inisialisasi SPI Hardware ESP32 untuk RFID
spi = SPI(2, baudrate=1000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
rfid = MFRC522(spi=spi, gpioCs=5, gpioRst=22)

print("--- MULAI SISTEM ABSENSI ---")
print("Tempelkan kartu ke reader...")

while True:
    (status, tag_type) = rfid.request(rfid.REQIDL)
    
    # Jika kartu terdeteksi oleh request
    if status == rfid.OK:
        (status, raw_uid) = rfid.anticoll()
        
        # Jika proses pembacaan UID (anticoll) berhasil
        if status == rfid.OK and raw_uid:
            uid_hex = "0x" + "".join(["%02X" % x for x in raw_uid[:4]])
            print(">>> KARTU TERBACA! UID:", uid_hex)
            
            # Tampilkan UID ke layar LCD
            lcd.clear()
            lcd.putstr("Terbaca:\n" + uid_hex)
            
            time.sleep(2)
            
            # Kembalikan tampilan LCD ke standby
            lcd.clear()
            lcd.putstr("Sistem Siap!\nTempelkan Kartu")
        else:
            # Jika request OK tapi anticoll gagal/goyang
            print("Kartu terdeteksi, tetapi gagal membaca UID (Tempel lebih dekat)...")
            lcd.clear()
            lcd.putstr("Gagal Baca UID\nTempel Dekat")
            time.sleep(0.5)
            lcd.clear()
            lcd.putstr("Sistem Siap!\nTempelkan Kartu")
            
    time.sleep_ms(50)