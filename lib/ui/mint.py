import re
from lib.graphical.kitty import Kitty, Color
from utils import VariableUtils, ObjectUtils

from config import DisplayConf
from utils import DriverUtils, AppUtils
Gpu = DriverUtils.load('gpu', 'ILI9488', 'Gpu')
gpu = Gpu(DisplayConf.resolution, DisplayConf.rotation)
gpu.display_off()
gpu.display_on()

class Mint:
    def __init__(self, mml, gpu):
        self.mml_parser = MMLParser()
        self.parsed     = None
        self.mml        = None
        self.kitty      = Kitty(gpu)
        self.set_mml(mml)
    
    def draw_elements(self, tags, level=0, last_pos={'x': 0, 'y': 0}):
        indent = "  " * level
        
        for tag in tags:
            attrs    = tag['attributes']
            x        = int(VariableUtils.key_nvl(attrs, 'x', 0))+last_pos['x']
            y        = int(VariableUtils.key_nvl(attrs, 'y', 0))+last_pos['y']
            children = tag['children']
            element  = VariableUtils.key_nvl(attrs, 'element', None)
            tag_name = tag['tag_name']
            
            print(f"{indent}Tag: {tag['tag_name']} Last: {last_pos} Current: x:{x} y:{y} Attrs: {attrs}")
            
            
            if not element:
                Element = ObjectUtils.get_class_by_name(tag_name[0].upper() + tag_name[1:], globals())
                element = Element(attrs)
            
            element.draw(self.kitty)
            
            if children:
                self.draw_elements(children, level+1, {'x': x, 'y': y})
    
    def draw(self):
        self.draw_elements(self.parsed)
    
    def set_prop_by_name(self):
        pass
    
    def set_prop_by_id(self):
        pass
    
    def set_mml(self, mml):
        if(mml == None):
            self.parsed = None
            self.mml    = None
        else:
            self.parsed = self.mml_parser.parse(mml)
            self.mml    = mml

class MMLParser:
    def __init__(self):
        pass
    
    def _find_tag(self, pos, mml):
        tag_start = mml.find('<', pos)
        if tag_start == -1:
            return -1, ''
        
        tag_end = mml.find('>', tag_start)
        if tag_end == -1:
            return -1, ''
    
        return tag_end, mml[tag_start + 1:tag_end].strip()
    
    def _parse_content(self, content):
        opens    = not content.startswith('/')
        tag      = content.lstrip('/')
        parts    = tag.split(' ', 1)
        tag_name = parts[0]
        
        attributes = {}
        if len(parts) > 1:
            attributes_str = parts[1]
            attributes_arr = attributes_str.split(' ')
            for attribute_str in attributes_arr:
                
                if '=' in attribute_str:
                    name, value = attribute_str.split('=', 1)
                    attributes[name] = value
        
        return {'opens': opens, 'tag_name': tag_name, 'attributes': attributes}
    
    def parse(self, mml):
        pos = 0
        root = []
        stack = []
        
        while True:
            pos, content = self._find_tag(pos, mml)
            if pos == -1:
                break

            tag = self._parse_content(content)
            
            if tag['opens']:
                new_tag = {'tag_name': tag['tag_name'], 'attributes': tag['attributes'], 'children': []}
                if stack:
                    stack[-1]['children'].append(new_tag)
                else:
                    root.append(new_tag)
                stack.append(new_tag)
            else:
                stack.pop()
        
        return root
    
class Element:
    def __init__(self, attributes):
        self.attributes = attributes
    
    def get_attribute(self, attribute):
        try:
            value = self.attributes[attribute]
        except KeyError:
            value = None
    
    def set_attribute(self, attribute, value):
        self.attributes[attribute] = value
    
    def delete_attribute(self, attribute):
        del self.attributes[attribute]
    
    def draw(self):
        pass

class View(Element):
    def draw(self, graph_lib):
        x = int(VariableUtils.key_nvl(self.attributes, 'x', 0))
        y = int(VariableUtils.key_nvl(self.attributes, 'y', 0))
        w = int(VariableUtils.key_nvl(self.attributes, ['width'], 1))
        h = int(VariableUtils.key_nvl(self.attributes, ['height'], 1))
        c = Color.hex('#FFFFFF')
        bc = Color.hex('#000000')
        r  = int(VariableUtils.key_nvl(self.attributes, ['radius'], 0))
        
        graph_lib.draw_box(x, y, w, h, c, bc, r)

class Text(Element):
    def draw(self, graph_lib):
        pass

mml_string = '''
<view x=50 y=50 width=200 height=200 radius=30>
    <text x=10 y=10 value=teste></text>
</view>
'''

#parser = MMLParser()
#parsed_mml = parser.parse(mml_string)
#print(parsed_mml)

mint = Mint(mml_string, gpu)

import time
start_time = time.ticks_ms()
mint.draw()
print("--- %s ms ---" % (time.ticks_ms() - start_time))


