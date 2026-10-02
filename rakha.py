from mfrc522 import MFRC522
from machine import Pin, SPI, PWM
import time

# SPI Hardware ESP32
spi = SPI(2, baudrate=1000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23), miso=Pin(19))

rfid = MFRC522(spi=spi, gpioCs=5, gpioRst=22)

# Inisialisasi Buzzer pada Pin 13
buzzer = PWM(Pin(13))
buzzer.duty(0) # Pastikan buzzer mati saat awal

def beep():
    """Fungsi buzzer dengan frekuensi lebih nyaring (2700 Hz)"""
    buzzer.freq(2700)   # Frekuensi diubah dari 1000 Hz ke 2700 Hz
    buzzer.duty(512)    # Tetap di 50% untuk amplitudo maksimal
    time.sleep(0.15)
    buzzer.duty(0)

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
            
            # Panggil fungsi buzzer saat berhasil membaca UID
            beep()
            
            time.sleep(1)
        else:
            # Jika request OK tapi anticoll gagal/goyang
            print("Kartu terdeteksi, tetapi gagal membaca UID (Coba tempel lebih dekat)...")
            time.sleep(0.5)
            
    time.sleep_ms(50)