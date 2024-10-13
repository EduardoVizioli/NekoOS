class DisplayConf:
    resolution = const((480, 320))
    rotation   = const(270)

class DriversConf:
    gpu = 'ILI9488'
    battery = 'pico_vsys'

class AppsConf:
    directory = 'apps'
    sd_directory = 'sd/apps'
    sys_directory = 'system_apps'
    home_app = 'vanilla'
    status_bar_app = 'azuki'