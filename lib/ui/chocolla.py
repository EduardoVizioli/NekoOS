from lib.graphical.kitty import Color

class Position():
    def __init__(self, x, y, width, height):
        self.x      = x
        self.y      = y
        self.width  = width
        self.height = height
    
    def get_data(self):
        return self.x, self.y, self.width, self.height

class Element():
    def __init__(self, position, id, class_ = None, properties = {}):
        self.position       = position
        self.last_position  = None
        self.children       = []
        self.properties     = {'id':id,
                               'class':class_,
                               'redraw_color':'#000000',
                               'radius': None,
                               'touch_event':None,
                               'h_anchor':'left',
                               'v_anchor':'top'}
        self.set_props(properties)
        self.default_redraw_props = ['redraw_color', 'radius', 'h_anchor', 'v_anchor']
        self.redraw_props   = []
        self.needs_to_draw  = True
        self.on_load()
    
    def get_redraw_props(self):
        return self.default_redraw_props + self.redraw_props
    
    def set_redraw_props(self, props):
        self.redraw_props = props
    
    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, index):
        return self.children.pop(index)
    
    def get_child(self, index):
        return self.children[index]
    
    def get_children(self):
        return self.children

    def calculate_relative_position(self, parent_position):
        x, y, width, height = parent_position.get_data()
        
        if self.get_prop('h_anchor') == 'left':
            x = self.position.x + x
        elif self.get_prop('h_anchor') == 'right':
            x = x + width - self.position.width - self.position.x
        elif self.get_prop('h_anchor') == 'center':
            x = x + ((width - self.position.width)//2)
        
        if self.get_prop('v_anchor') == 'top':
            y = self.position.y + y
        elif self.get_prop('v_anchor') == 'bottom':
            y = y + height - self.position.height - self.position.y
        elif self.get_prop('v_anchor') == 'center':
            y = y + ((height - self.position.height)//2)
        
        width  = self.position.width
        height = self.position.height

        return Position(x, y, width, height)
    
    def areas_to_clear(self, position, last_position):
        if last_position == None:
            return
        
        left_x   = position.x
        right_x  = position.x + position.width
        top_y    = position.y
        bottom_y = position.y + position.height
        
        last_left_x   = last_position.x
        last_right_x  = last_position.x + last_position.width
        last_top_y    = last_position.y
        last_bottom_y = last_position.y + last_position.height
        
        last_width = last_position.width
        last_height = last_position.height
        
        positions = []
        
        if (left_x > last_right_x or top_y > last_bottom_y or right_x < last_left_x or bottom_y < last_top_y):
            yield last_position
        else:
            x = 1
            y = 1
            width = 1
            height = 1
            
            if(left_x > last_left_x):
                x = last_left_x
                y = last_top_y
                width = left_x - last_left_x
                height = last_height
                
                yield Position(x, y, width, height)
                
            elif(left_x < last_left_x):
                x = right_x
                y = last_top_y
                width = last_right_x - right_x
                height = last_height
                
                yield Position(x, y, width, height)
            
            if(top_y > last_top_y):
                x = last_left_x
                y = last_top_y
                width = last_width
                height = top_y - last_top_y
                
                yield Position(x, y, width, height)
                
            elif(top_y < last_top_y):
                x = left_x
                y = bottom_y
                width = last_width
                height = last_bottom_y - bottom_y
                
                yield Position(x, y, width, height)
    
    def draw_clear(self, gl, position, last_position):
        for pos in self.areas_to_clear(position, last_position):
            gl.draw_box(pos.x, pos.y, pos.width, pos.height, Color.hex(self.get_prop('redraw_color')))
    
    def draw(self, graphics_library, parent_position = Position(0, 0, 0, 0)):
        redraw = self.needs_to_draw
        relative_position = self.calculate_relative_position(parent_position)
        
        if not redraw:
            for child in self.get_children():
                child.draw(graphics_library, relative_position)            
            return
        
        print(self.get_prop('id'), relative_position.x, relative_position.y, relative_position.width, relative_position.height)
        
        self._draw(relative_position, graphics_library)
        self.draw_clear(graphics_library, relative_position, self.last_position)
        self.unmark_for_redraw()
        
        for child in self.get_children():
            child.mark_for_redraw()
            child.draw(graphics_library, relative_position)
        
        self.draw_clear(graphics_library, relative_position, self.last_position)
        self.last_position = Position(relative_position.x, relative_position.y, relative_position.width, relative_position.height)
        
    def mark_for_redraw(self):
        self.needs_to_draw = True
    
    def unmark_for_redraw(self):        
        self.needs_to_draw = False
    
    def set_prop(self, property, value):
        if (property in self.get_redraw_props()):
            self.mark_for_redraw()

        self.properties[property] = value
        self._set_prop(property, value)
    
    def set_children_prop(self, property, value):
        self.set_prop(self, property, value)
        
        for child in self.get_children():
            child.set_children_prop(self, property, value)
    
    def _set_prop(self, property, value):
        pass
    
    def set_props(self, props):
        for prop in props:
            value = props[prop]
            self.set_prop(prop, value)

    def get_prop(self, prop):
        try:
            return self.properties[prop]
        except KeyError:
            return None
        
    def on_load(self):
        pass

    def set_x(self, x):
        self.position.x = x    
        self.mark_for_redraw()

    def set_y(self, y):
        self.position.y = y
        self.mark_for_redraw()

    def set_width(self, width):
        self.position.width = width
        self.mark_for_redraw()

    def set_height(self, height):
        self.position.height = height
        self.mark_for_redraw()
        
    def check_touch(self, event, parent_position = None):
        touch_event = self.properties['touch_event']
        
        x = event[0]
        y = event[1]
        
        pos = self.calculate_relative_position(parent_position)
        
        if x >= pos.x and x <= pos.x + pos.width and y >= pos.y and y <= pos.y + pos.height:
            if touch_event == None:
                self.proc_touch_events(event, pos)
            else:
                touch_event(event)
                return True
        return False
    
    def proc_touch_events(self, event, parent_position = None):
        if parent_position == None:
            parent_position = self.position
        
        for child in self.children:
            child.check_touch(event, parent_position)
    
class Document(Element):
    def _draw(self, pos, gl):
        pass
    
    def get_by_id(self, id):
        for child in self.children:
            if child.get_prop('id') == id:
                return child

class Div(Element):
    def on_load(self):
        self.set_redraw_props(['color', 'redraw_color'])

    def _draw(self, pos, gl):
        x = pos.x
        y = pos.y
        w = pos.width
        h = pos.height
        c = Color.hex(self.get_prop('color'))
        bc = Color.hex(self.get_prop('redraw_color'))
        r  = self.get_prop('radius')
        
        gl.draw_box(x, y, w, h, c, bc, r)

class Text(Element):
    def on_load(self):
        self.set_redraw_props(['color', 'content', 'font'])
    
    def _draw(self, pos, gl):
        x = pos.x
        y = pos.y
        text = self.get_prop('content')
        font = self.get_prop('font')
        color = Color.hex(self.get_prop('color'))
        background = Color.hex(self.get_prop('redraw_color'))
        landscape = False
        spacing = self.get_prop('spacing')
        transparent = False
        
        print(x, y, text, font, color, background, landscape, spacing, transparent)
        gl.draw_text(x, y, text, font, color, background, landscape, spacing, transparent)
    
    def set_prop(self, property, value):
        if property == 'content':
            font = self.get_prop('font')
            width, height = font.get_text_width_height(value)
            self.set_width(width)
            self.set_height(height)
            
        super().set_prop(property, value)
    
class Button(Element):
    def on_load(self):
        id = self.get_prop('id')
        self.body = Div(self.position
                       ,id+'_body'
                       ,{
                            'color': self.get_prop('color'),
                            'redraw_color': self.get_prop('redraw_color')
                        })
        
        self.text = Text(self.position
                        ,id+'_text'
                        ,{
                            'redraw_color': self.get_prop('color'),
                            'color': self.get_prop('text_color'),
                            'content':self.get_prop('content'),
                            'font':self.get_prop('font')
                        })
        
        self.add_child(self.body)
        self.add_child(self.text)

        self.div_props = [
            ['color', 'color'],
            ['redraw_color', 'redraw_color'],
        ]
        self.text_props = [
            ['redraw_color', 'color'],
            ['color', 'text_color'],
            ['content', 'content'],
            ['font', 'font']
        ]

    def set_prop(self, property, value):
        for prop in self.div_props:
            if prop[1] == property:
                self.body.set_prop(prop[0], prop[1])
                break

        for prop in self.text_props:
            if prop[1] == property:
                self.text.set_prop(prop[0], prop[1])
                break

        self.set_prop(self, property, value)
    
class List(Element):
    def on_load(self):
        self.set_redraw_props('color', 'buttons_color', 'redraw_color')
        self.items = []
        
    def _draw(self, pos, gl):
        pass
    
