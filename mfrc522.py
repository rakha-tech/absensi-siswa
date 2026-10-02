from machine import Pin, SPI

class MFRC522:
    OK = 0
    NOTAGERR = 1
    ERR = 2

    REQIDL = 0x26
    PICC_ANTICOLL = 0x93

    def __init__(self, spi, gpioCs, gpioRst):
        self.spi = spi
        self.cs = Pin(gpioCs, Pin.OUT)
        self.rst = Pin(gpioRst, Pin.OUT)
        self.cs.value(1)
        self.rst.value(1)
        self.init()

    def _wreg(self, reg, val):
        self.cs.value(0)
        self.spi.write(b'%c%c' % ((reg << 1) & 0x7E, val))
        self.cs.value(1)

    def _rreg(self, reg):
        self.cs.value(0)
        self.spi.write(b'%c' % (((reg << 1) & 0x7E) | 0x80))
        val = self.spi.read(1)
        self.cs.value(1)
        return val[0]

    def _set_bit_mask(self, reg, mask):
        self._wreg(reg, self._rreg(reg) | mask)

    def _clear_bit_mask(self, reg, mask):
        self._wreg(reg, self._rreg(reg) & (~mask))

    def init(self):
        self.reset()
        self._wreg(0x2A, 0x8D)
        self._wreg(0x2B, 0x3E)
        self._wreg(0x2D, 30)
        self._wreg(0x2C, 0)
        self._wreg(0x15, 0x40)
        self._wreg(0x11, 0x3D)
        self.antenna_on()

    def reset(self):
        self._wreg(0x01, 0x0F)

    def antenna_on(self, on=True):
        if on:
            # Perbaikan bitmask: Aktifkan TxControlReg (0x14) jika bit 0 dan 1 belum set
            if (self._rreg(0x14) & 0x03) != 0x03:
                self._set_bit_mask(0x14, 0x03)
        else:
            self._clear_bit_mask(0x14, 0x03)

    def _tcmd(self, cmd, send_data):
        back_data = []
        back_len = 0
        status = self.ERR
        irq_en = 0x77
        wait_irq = 0x30

        self._wreg(0x02, irq_en | 0x80)
        self._clear_bit_mask(0x04, 0x80)
        self._set_bit_mask(0x0A, 0x80)
        self._wreg(0x01, 0x00)

        for i in range(len(send_data)):
            self._wreg(0x09, send_data[i])

        self._wreg(0x01, cmd)

        if cmd == 0x0C:
            self._set_bit_mask(0x0D, 0x80)

        i = 2000
        while True:
            n = self._rreg(0x04)
            i -= 1
            if not ((i != 0) and not (n & 0x01) and not (n & wait_irq)):
                break

        self._clear_bit_mask(0x0D, 0x80)

        if i != 0:
            if (self._rreg(0x06) & 0x1B) == 0x00:
                status = self.OK
                if n & irq_en & 0x01:
                    status = self.NOTAGERR

                if cmd == 0x0C:
                    n = self._rreg(0x0A)
                    last_bits = self._rreg(0x0C) & 0x07
                    if last_bits != 0:
                        back_len = (n - 1) * 8 + last_bits
                    else:
                        back_len = n * 8
                    if n == 0:
                        n = 1
                    if n > 16:
                        n = 16
                    for _ in range(n):
                        back_data.append(self._rreg(0x09))
            else:
                status = self.ERR

        return status, back_data, back_len

    def request(self, mode):
        self._wreg(0x0D, 0x07)
        status, back_data, back_bits = self._tcmd(0x0C, [mode])
        if status != self.OK or back_bits != 0x10:
            status = self.ERR
        return status, back_bits

    def anticoll(self):
        self._wreg(0x0D, 0x00)
        ser_num = [self.PICC_ANTICOLL, 0x20]
        status, back_data, back_bits = self._tcmd(0x0C, ser_num)
        if status == self.OK and len(back_data) >= 4:
            status = self.OK
        else:
            status = self.ERR
        return status, back_data