from lib.graphical.kitty import Font
from lib.ui.chocolla import *
from utils import Utils
from lib.system.apps import *

class MainScreen(BaseScreen):
    def on_start(self):
        document = self.system.get_app_document()
        self.div_back = Div(Position(0, 0, 480, 290), 'background')
        self.div_back.set_prop('color', '#000000')
        document.add_child(self.div_back)
    
    def on_update(self, events):
        pass

class App(BaseApp):
    def on_start(self):
        self.add_screen(MainScreen, 'main')
        
    def on_update(self, events):
        pass
        
