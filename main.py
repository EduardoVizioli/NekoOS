from config import DisplayConf, AppsConf
from lib.graphical.kitty import Kitty, Color
from lib.ui.chocolla import Document, Position
from utils import DriverUtils, AppUtils
import _thread

#Load Drivers
Gpu = DriverUtils.load('gpu', 'ILI9488', 'Gpu')
gpu = Gpu(DisplayConf.resolution, DisplayConf.rotation) # type: ignore
battery = DriverUtils.load('battery', 'pico_vsys', 'Battery')
sdcard = DriverUtils.load('storage', 'sdcard', 'SDCard')
Touch  = DriverUtils.load('touch', 'xpt2046', 'Touch')
touch = Touch() # type: ignore

class GpuController:
    def __init__(self, system):
        self.system = system
        self.running = False
    
    def start(self):
        print('Starting GPU controller')
        
        self.running = True
        while self.running:
            self.system.status_document.draw(self.system.kitty_gl)
            self.system.app_document.draw(self.system.kitty_gl)
    
        try:
            pass
        except Exception as e:
            print('A critial error ocurred while rendering.')
            print(e)
            self.system.load_home_app()
            
    def stop(self):
        self.running = False

class System:
    def __init__(self, gpu, battery, sdcard, touch):
        self.started  = False
        
        self.battery  = battery
        self.gpu      = gpu
        self.sdcard   = sdcard
        self.touch    = touch
        self.kitty_gl = Kitty(gpu)
        
        self.status_document = Document(Position(0, 0, 480, 30), 'status_doc')
        self.app_document    = Document(Position(0, 30, 480, 290), 'app_doc')
        
        self.load_home_app()
        self.load_status_bar()
        
        self.gpu_controller = self.start_gpu_controller()
        self.start_mainloop()
        
    def load_app(self, directory, name):
        print('Loading %s.%s...'%(directory, name))
        App = AppUtils.load('%s.%s'%(directory, name), 'App')
        app = App(self)
        print('%s.%s Loaded'%(directory, name))
        
        return app
    
    def load_home_app(self):
        print('Loading home app')
        self.start_app(AppsConf.sys_directory, AppsConf.home_app)
        print('Home app loaded')
    
    def load_status_bar(self):
        print('Loading statusbar')
        self.status_bar = self.load_app(AppsConf.sys_directory, AppsConf.status_bar_app)
        print('Statusbar loaded')
    
    def start_app(self, directory, app_name):
        print('Starting ' + app_name)
        self.app_document    = Document(Position(0, 30, 480, 290), 'app_doc')
        self.running_app = self.load_app(directory, app_name)
        print(app_name + ' started')
    
    def get_installed_apps(self):
        return AppUtils.list_apps(AppsConf.directory)
    
    def get_current_app(self):
        return self.running_app
    
    def get_app_document(self):
        return self.app_document
    
    def get_status_document(self):
        return self.status_document

    def start_gpu_controller(self):
        gpu_controller = GpuController(self)
        _thread.start_new_thread(gpu_controller.start, ())
        return gpu_controller
    
    def start_mainloop(self):
        self.started = True
        print('System boot finished Nya!')
        
        while self.started:
            touch_event = self.touch.single_touch()
            
            if touch_event != None:
                self.app_document.proc_touch_events(touch_event)
                self.status_document.proc_touch_events(touch_event)
                
            self.status_bar.process(touch_event)
            self.running_app.process(touch_event)

    def stop(self):
        system.started = False

system = System(gpu, battery, sdcard, touch)