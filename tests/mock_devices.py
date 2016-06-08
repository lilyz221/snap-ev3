import os
import shutil


class MockDevice(object):

    def __init__(self, device_root_path, class_path, base_name):
        class_dir = os.path.join(device_root_path, class_path)
        if not os.path.exists(class_dir):
            os.mkdir(class_dir, 0755)
        for num in range(0,99):
            device_dir = os.path.join(class_dir, base_name + str(num))
            if not os.path.exists(device_dir):
                os.mkdir(device_dir, 0755)
                self.path = device_dir
                break
        self.attributes = set()
        self.readonly = set()
    
    def __del__(self):
        if self.path:
            shutil.rmtree(self.path)

    def add_attribute(self, name, init=None, readonly=True):
        if name in self.attributes:
            raise KeyError("Attribute '{}' already exists".format(name))
        attrib_dir = os.path.join(self.path, os.path.dirname(name))
        if not os.path.exists(attrib_dir):
            os.makedirs(attrib_dir, 0755)
        attrib_file = os.path.join(self.path, name)
        with open(attrib_file, "w") as f:
            if init is not None:
                f.write(str(init))
        self.attributes.add(name)
        if readonly:
            self.readonly.add(name)

    def read(self, name):
        if name not in self.attributes:
            raise KeyError("Attribute '{}' does not exist".format(name))
        attrib_file = os.path.join(self.path, name)
        with open(attrib_file, "r") as f:
            return f.read()

    def write(self, name, value):
        if name not in self.attributes:
            raise KeyError("Attribute '{}' does not exist".format(name))
        if name in self.readonly:
            raise KeyError("Attribute '{}' is read-only".format(name))
        attrib_file = os.path.join(self.path, name)
        with open(attrib_file, "w") as f:
            f.seek(0)
            f.write(str(value))
            f.truncate()
            
            
