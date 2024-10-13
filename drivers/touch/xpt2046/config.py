class SpiConf:
    dc       = None
    cs       = const(9)
    mosi     = const(10)
    clk      = const(12)
    rst      = None
    miso     = const(11)
    baudrate = const(500_000)
    number   = -1