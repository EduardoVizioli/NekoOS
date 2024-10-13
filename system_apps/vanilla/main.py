from lib.graphical.kitty import Color, Font
from lib.ui.chocolla import *
from utils import Utils
import random
from lib.system.apps import *
from config import AppsConf

r = lambda: random.randint(0,255)

class MainScreen(BaseScreen):
    def on_start(self):
        self.icon_size = 40
        self.dock_spacing = 10
        self.dock_height = 50
        self.apps_list = self.system.get_installed_apps()
        self.app_icons = {}
        
        self.font = Font('./assets/fonts/ArcadePix9x11.cff', 9, 11)
        document = self.system.get_app_document()
        self.div_back = Div(Position(0, 0, 480, 290), 'background')
        self.div_back.set_prop('color', '#01547a')
        document.add_child(self.div_back)
        
        dock_width = ((self.icon_size + self.dock_spacing//2) * len(self.apps_list)) + self.dock_spacing//2
        
        self.div_dock = Div(Position(0, 10, dock_width, self.dock_height), 'dock')
        self.div_dock.set_prop('radius', 15)
        self.div_dock.set_prop('color', '#FFFFFF')
        self.div_dock.set_prop('redraw_color', '#01547a')
        self.div_dock.set_prop('h_anchor', 'center')
        self.div_dock.set_prop('v_anchor', 'bottom')
        self.div_back.add_child(self.div_dock)
        
        cnt = 0
        for app in self.apps_list:
            color = '#%02X%02X%02X' % (r(),r(),r())
            div_app = Div(Position((self.dock_spacing//2) + ((cnt * (self.icon_size + (self.dock_spacing//2)))), 0, self.icon_size, self.icon_size), 'app_icon_'+app)
            print('app_icon_'+app)
            div_app.set_prop('radius', 15)
            div_app.set_prop('color', color)
            div_app.set_prop('redraw_color', '#FFFFFF')
            div_app.set_prop('v_anchor', 'center')
            div_app.set_prop('touch_event', lambda event:
                self.system.start_app(AppsConf.directory, app)
            )
            self.app_icons[app] = div_app
            self.div_dock.add_child(div_app)
            
            cnt += 1
    
    def on_update(self, events):
        pass

class App(BaseApp):
    def on_start(self):
        self.add_screen(MainScreen, 'main')
        
    def on_update(self, events):
        pass
        