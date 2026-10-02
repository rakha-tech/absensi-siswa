from mfrc522 import MFRC522
from machine import Pin, SPI
import time

# SPI Hardware ESP32
spi = SPI(2, baudrate=1000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))

rfid = MFRC522(spi=spi, gpioCs=5, gpioRst=22)

print("--- MULAI TES MEMBACA KARTU ---")
print("Tempelkan kartu dan perhatikan terminal...")

while True:
    (status, tag_type) = rfid.request(rfid.REQIDL)
    
    # Jika kartu terdeteksi oleh request
    if status == rfid.OK:
        (status, raw_uid) = rfid.anticoll()
        
        # Jika proses pembacaan UID (anticoll) berhasil
        if status == rfid.OK and raw_uid:
            uid_hex = "0x" + "".join(["%02X" % x for x in raw_uid[:4]])
            print(">>> KARTU TERBACA! UID:", uid_hex)
            time.sleep(1)
        else:
            # Jika request OK tapi anticoll gagal/goyang
            print("Kartu terdeteksi, tetapi gagal membaca UID (Coba tempel lebih dekat)...")
            time.sleep(0.5)
            
    time.sleep_ms(50)