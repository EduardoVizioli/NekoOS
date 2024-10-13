class SpiConf:
    dc       = const(15)
    cs       = const(13)
    mosi     = const(7)
    clk      = const(6)
    rst      = const(14)
    miso     = None
    baudrate = const(80_000_000)
    number   = 0