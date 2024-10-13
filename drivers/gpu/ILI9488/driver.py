from time import sleep_ms
from math import cos, sin, pi, radians
import ustruct
from machine import Pin, SPI
from .config import SpiConf

class Gpu(object):
    """Serial interface for 18-bit color (6-6-6 RGB) IL9488 display.

    Note:  All coordinates are zero based.
    """

    # Command constants from ILI9488 datasheet
    NOP = const(0x00)  # No-op
    SWRESET = const(0x01)  # Software reset
    SLPIN = const(0x10)  # Enter sleep mode
    SLPOUT = const(0x11)  # Exit sleep mode
    INVOFF = const(0x20)  # Display inversion off
    INVON = const(0x21)  # Display inversion on
    GAMMASET = const(0x26)  # Gamma set
    DISPLAY_OFF = const(0x28)  # Display off
    DISPLAY_ON = const(0x29)  # Display on
    SET_COLUMN = const(0x2A)  # Column address set
    SET_PAGE = const(0x2B)  # Page address set
    WRITE_RAM = const(0x2C)  # Memory write
    READ_RAM = const(0x2E)  # Memory rea
    VSCRDEF = const(0x33)  # Vertical scrolling definition
    MADCTL = const(0x36)  # Memory access control
    VSCRSADD = const(0x37)  # Vertical scrolling start address
    PIXFMT = const(0x3A)  # COLMOD: Pixel format set
    FRMCTR1 = const(0xB1)  # Frame rate control (In normal mode/full colors)
    FRMCTR2 = const(0xB2)  # Frame rate control (In idle mode/8 colors)
    FRMCTR3 = const(0xB3)  # Frame rate control (In partial mode/full colors)
    INVCTR = const(0xB4)  # Display inversion control
    DFUNCTR = const(0xB6)  # Display function control
    PWCTR1 = const(0xC0)  # Power control 1
    PWCTR2 = const(0xC1)  # Power control 2
    PWCTRA = const(0xCB)  # Power control A
    PWCTRB = const(0xCF)  # Power control B
    VMCTR1 = const(0xC5)  # VCOM control 1
    VMCTR2 = const(0xC7)  # VCOM control 2
    GMCTRP1 = const(0xE0)  # Positive gamma correction
    GMCTRN1 = const(0xE1)  # Negative gamma correction
    DTCA = const(0xE8)  # Driver timing control A
    DTCB = const(0xEA)  # Driver timing control B
    POSC = const(0xED)  # Power on sequence control
    ENABLE3G = const(0xF2)  # Enable 3 gamma control
    PUMPRC = const(0xF7)  # Pump ratio control
    INMODC = const(0xB0) # Interface Mode Control
    EMODSET = const(0xb7) #Entry Mode Set

    #TODO Verify codes
    ROTATIONS = {
        0: 0x88,
        90: 0xE8,
        180: 0x48,
        270: 0x28
    }
    
    def __init__(self, resolution, rotation = 0):
        """Initialize Driver.
        Args:
            resolution (tupple): Tupple containing the resolution (width, height)
            rotation (Optional int): Rotation must be 0 default, 90. 180 or 270
        """
        
        self.spi = SPI(SpiConf.number, baudrate=SpiConf.baudrate, mosi=Pin(SpiConf.mosi), sck=Pin(SpiConf.clk))
        
        self.cs = Pin(SpiConf.cs)
        self.dc = Pin(SpiConf.dc)
        self.rst = Pin(SpiConf.rst)
        self.width = resolution[0]
        self.height = resolution[1]
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=1)
        
        if rotation not in self.ROTATIONS.keys():
            raise RuntimeError('Rotation must be 0, 90, 180 or 270.')
        else:
            self.rotation = self.ROTATIONS[rotation]
        
        self.reset()
        
        # Send initialization commands
        self.write_cmd(self.SWRESET)  # Software reset
        sleep_ms(100)
        self.write_cmd(self.GMCTRP1, 0x00, 0x03, 0x09, 0x08, 0x16, 0x0A, 0x3F, 0x78, 0x4C, 0x09, 0x0A, 0x08, 0x16, 0x1A, 0x0F) #Positive gamma control
        self.write_cmd(self.GMCTRN1, 0x00, 0x16, 0x19, 0x03, 0x0F, 0x05, 0x32, 0x45, 0x46, 0x04, 0x0E, 0x0D, 0x35, 0x37, 0x0F) #Negative gamma control
        self.write_cmd(self.PWCTR1, 0x17, 0x15) # Power control 1
        self.write_cmd(self.PWCTR2, 0x41) # Power control 2
        self.write_cmd(self.VMCTR1, 0x00, 0x12, 0x80) # VCOM control 1
        
        #TODO Verify codes
        self.write_cmd(self.MADCTL, self.rotation) # Memory access control
        self.write_cmd(self.PIXFMT, 0x66) # Pixel format
        self.write_cmd(self.INMODC, 0x00) # Interface Mode Control
        self.write_cmd(self.FRMCTR1, 0xA0) # Frame Rate Control 1
        self.write_cmd(self.DFUNCTR, 0x02, 0x02) # Display function control
        self.write_cmd(self.EMODSET, 0xC6) # Entry Mode Set
        self.write_cmd(self.PUMPRC, 0xA9, 0x51, 0x2C, 0x02)  # Pump ratio control
        self.write_cmd(self.SLPOUT)  # Exit sleep
        sleep_ms(120)
        self.write_cmd(self.DISPLAY_ON)  # Display on
        self.clear()
    
    def block(self, x0, y0, x1, y1, data):
        """Write a block of data to display.

        Args:
            x0 (int):  Starting X position.
            y0 (int):  Starting Y position.
            x1 (int):  Ending X position.
            y1 (int):  Ending Y position.
            data (bytes): Data buffer to write.
        """
        self.write_cmd(self.SET_COLUMN, *ustruct.pack(">HH", x0, x1))
        self.write_cmd(self.SET_PAGE, *ustruct.pack(">HH", y0, y1))

        self.write_cmd(self.WRITE_RAM)
        
        self.write_data(data)

    def cleanup(self):
        """Clean up resources."""
        self.clear()
        self.display_off()
        self.spi.deinit()
        print('display off')

    def clear(self, color=0, hlines=8):
        """Clear display.

        Args:
            color (Optional int): RGB888 color value (Default: 0 = Black).
            hlines (Optional int): # of horizontal lines per chunk (Default: 8)
        Note:
            hlines was introduced to deal with memory allocation on some
            boards.  Smaller values allocate less memory but take longer
            to execute.  hlines must be a factor of the display height.
            For example, for a 240 pixel height, valid values for hline
            would be 1, 2, 4, 5, 8, 10, 16, 20, 32, 40, 64, 80, 160.
            Higher values may result in memory allocation errors.
        """

        w = self.width
        h = self.height
        assert hlines > 0 and h % hlines == 0, ("hlines must be a non-zero factor of height.")
        # Clear display
        if color:
            line = color.to_bytes(3, 'big') * (w * hlines)
        else:
            line = bytearray(w * 3 * hlines)
        for y in range(0, h, hlines):
            self.block(0, y, w - 1, y + hlines - 1, line)
            
    def display_off(self):
        """Turn display off."""
        self.write_cmd(self.DISPLAY_OFF)

    def display_on(self):
        """Turn display on."""
        self.write_cmd(self.DISPLAY_ON)
        
    def reset(self):
        """Perform reset: Low=initialization, High=normal operation."""
        self.rst(0)
        sleep_ms(50)
        self.rst(1)
        sleep_ms(50)

    def write_cmd(self, command, *args):
        """Write command to TFT.

        Args:
            command (byte): ILI9488 command code.
            *args (optional bytes): Data to transmit.
        """
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([command]))
        self.cs(1)
        # Handle any passed data
        if len(args) > 0:
            self.write_data(bytearray(args))
    
    def write_data(self, data):
        """Write data to TFT.

        Args:
            data (bytes): Data to transmit.
        """
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)
    