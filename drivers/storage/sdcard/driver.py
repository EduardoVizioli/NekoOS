from machine import Pin, SPI
from .config import SpiConf
from .sdcard import SDCard
import uos

class SDCard():
    def __init__(self, mount_point):
        self.spi = SPI(SpiConf.number, baudrate=SpiConf.baudrate, mosi=Pin(SpiConf.mosi), sck=Pin(SpiConf.clk))
        self.cs = self.cs = Pin(SpiConf.cs)

        # Initialize SD card
        sd = sdcard.SDCard(self.spi, self.cs)

        # Mount filesystem
        vfs = uos.VfsFat(sd)
        uos.mount(vfs, mount_point)
