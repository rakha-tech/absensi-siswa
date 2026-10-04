from lcd_api import LcdApi
import time

MASK_RS = 0x01
MASK_RW = 0x02
MASK_E  = 0x04
SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4

class I2cLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.backlight = True
        time.sleep_ms(20)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(5)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(1)
        self.hal_write_init_nibble(0x03)
        self.hal_write_init_nibble(0x02)
        cmd = self.LCD_FUNCTION
        if num_lines > 1:
            cmd |= self.LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)
        self.clear()
        self.hal_write_command(self.LCD_ENTRY_MODE | self.LCD_ENTRY_INC)
        LcdApi.__init__(self, num_lines, num_columns)

    def hal_write_init_nibble(self, nibble):
        byte = (nibble << SHIFT_DATA) | (int(self.backlight) << SHIFT_BACKLIGHT)
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))

    def hal_backlight_on(self):
        self.backlight = True
        self.i2c.writeto(self.i2c_addr, bytes([int(self.backlight) << SHIFT_BACKLIGHT]))

    def hal_backlight_off(self):
        self.backlight = False
        self.i2c.writeto(self.i2c_addr, bytes([int(self.backlight) << SHIFT_BACKLIGHT]))

    def hal_write_command(self, cmd):
        self.hal_write_byte(cmd, 0)

    def hal_write_data(self, data):
        self.hal_write_byte(data, MASK_RS)

    def hal_write_byte(self, data, mode):
        high = mode | (data & 0xF0) | (int(self.backlight) << SHIFT_BACKLIGHT)
        low = mode | ((data << 4) & 0xF0) | (int(self.backlight) << SHIFT_BACKLIGHT)
        self.i2c.writeto(self.i2c_addr, bytes([high | MASK_E, high]))
        self.i2c.writeto(self.i2c_addr, bytes([low | MASK_E, low]))