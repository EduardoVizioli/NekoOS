class SpiConf:
    dc       = None
    cs       = const(1)
    mosi     = const(3)
    clk      = const(2)
    rst      = None
    miso     = const(4)
    baudrate = const(1_000_000)
    number   = 1

class DirConf:
    mountPoint = '/sd'