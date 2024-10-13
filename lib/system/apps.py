class BaseApp():
    def __init__(self, system):
        self.system = system
        self.screens = {}
        self.screen = None
        self.document = system.get_app_document()
        self.on_start()
        self.set_screen('main')
    
    def on_start(self):
        pass
    
    def on_update(self, events):
        pass

    def save_state(self):
        pass
    
    def on_exit(self):
        pass
    
    def process(self, event):
        self.on_update(event)
        self.screen.on_update(event)

    def set_screen(self, name):
        try:
            self.screen = self.screens[name]
            self.screen.on_start()
        except KeyError as e:
            raise KeyError('Screen {0} does not exist in app'.format(name))
    
    def add_screen(self, screen, name):
        self.screens[name] = screen(self.system)

class BaseScreen():
    def __init__(self, system):
        self.system = system
        pass

    def on_update(self, events):
        pass

    def on_start(self):
        pass
