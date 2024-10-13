from lib.graphical.kitty import Color, Font
from lib.ui.chocolla import *
import time
from utils import Utils
import random
from lib.system.apps import *

r = lambda: random.randint(0,255)

class MainScreen(BaseScreen):
    def on_start(self):
        self.font = Font('./assets/fonts/ArcadePix9x11.cff', 9, 11)
        
        document = self.system.get_status_document()
        self.div_back = Div(Position(0, 0, 480, 30), 'background')
        self.div_back.set_prop('color', '#003E5A')
        document.add_child(self.div_back)
        
        self.div_bat = Div(Position(70, 5, 45, 20), 'batttery')
        #self.div_bat.set_prop('radius', 3)
        self.div_bat.set_prop('color', '#FFFFFF')
        self.div_bat.set_prop('redraw_color', '#555555')
        self.div_bat.set_prop('h_anchor', 'right')
        self.div_back.add_child(self.div_bat)
        
        self.num_bat = Text(Position(0, 0, 0, 0), 'num_battery')
        self.num_bat.set_props({'color':'#000000', 'redraw_color':'#FFFFFF', 'font':self.font, 'content': '0%', 'spacing':1, 'h_anchor':'center', 'v_anchor':'center'})
        self.div_bat.add_child(self.num_bat)
        
        self.div_clock = Div(Position(5, 5, 60, 20), 'clock')
        self.div_clock.set_props({'color':'#FFFFFF', 'redraw_color':'#555555', 'touch_event':self.touch_clock, 'h_anchor':'right'})
        self.div_back.add_child(self.div_clock)
        
        self.clock_text = Text(Position(0, 0, 0, 0), 'clock_text')
        self.clock_text.set_props({'color':'#000000', 'redraw_color':'#FFFFFF', 'font':self.font, 'content': '00:00', 'spacing':1, 'h_anchor':'center', 'v_anchor':'center'})
        self.div_clock.add_child(self.clock_text)
        
        self.div_home = Div(Position(5, 5, 20, 20), 'home_button')
        self.div_home.set_prop('color', '#FFFFFF')
        self.div_home.set_prop('redraw_color', '#555555')
        self.div_home.set_prop('touch_event', self.touch_home)
        self.div_back.add_child(self.div_home)
        
        self.last_percent = None
        self.last_time = (-1, -1, -1, -1, -1, -1, -1, -1)
        self.every = 10
        self.last_proc_time = time.time() - self.every

    def on_update(self, events):
        proc_time = time.time()
        
        if proc_time <= (self.last_proc_time + 10):
            return
        
        self.last_proc_time = proc_time
        
        bat = self.system.battery
        percent, volt = bat.measure()
        percent = str(int(percent))
        
        if percent != self.last_percent:
            self.last_percent = percent
            self.num_bat.set_prop('content', percent+'%')
        
        curr_time = time.localtime()
        
        if self.last_time[4] != curr_time[4]:
            self.last_time = curr_time
            hours = Utils.zfill(str(curr_time[3]), 2)
            minutes = Utils.zfill(str(curr_time[4]), 2)
            self.clock_text.set_prop('content', hours+':'+minutes)

    def touch_clock(self, event):
        color = '#%02X%02X%02X' % (r(),r(),r())
        self.div_clock.set_prop('color', color)
        self.clock_text.set_prop('redraw_color',color)
        
        print('event clock: ', event)
    
    def touch_home(self, event):
        self.system.load_home_app()

class App(BaseApp):
    def on_start(self):
        self.add_screen(MainScreen, 'main')
        
    def on_update(self, events):
        pass
        