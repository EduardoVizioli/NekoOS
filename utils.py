import sys
import gc
import os

class ModuleUtils:
    
    @staticmethod
    def import_module(path, args):
        module = __import__(path)
        classes = []
        
        for directory in path.split('.')[1:]:
            module = getattr(module, directory)
        
        for module_class in args:
            classes.append(getattr(module, module_class))
        
        return classes
        
class DriverUtils:
    
    @staticmethod
    def load(driver_type, name, *args):
        print('Loaded %s driver %s' % (driver_type, name))
        
        classes = ModuleUtils.import_module('drivers.%s.%s.driver' % (driver_type, name), args)
        
        if len(classes) == 1:
            return classes[0]
        else:
            return tuple(classes)
        
class AppUtils:
    
    @staticmethod
    def load(path, name):
        path = path.replace('/', '.') + '.main'
        app = ModuleUtils.import_module(path, [name])
        return app[0]
    
    @staticmethod
    def list_apps(path):
        return os.listdir('./'+path)
            
class Utils:
    
    @staticmethod
    def zfill(s, width):
        return '{:0>{w}}'.format(s, w=width)
    
    @staticmethod
    def ram_info():
        gc.collect()
        free  = gc.mem_free()
        aloc  = gc.mem_alloc()
        total = free + aloc
        
        return total, free, aloc
    
class VariableUtils:
    
    @staticmethod
    def key_nvl(value, keys, null_value):
        try:
            for key in keys:
                value = value[key]
            return value
        except KeyError:
            return null_value
    
class ObjectUtils:
    
    @staticmethod
    def get_class_by_name(class_name, caller_globals):
        return caller_globals.get(class_name)
        
