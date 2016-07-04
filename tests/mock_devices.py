import os
import shutil


class MockDevice(object):

    def __init__(self, device_root_path, class_path,
                 base_name, driver_name, port):

        self.attributes = set()
        self.path = None

        class_dir = os.path.join(device_root_path, class_path)
        if not os.path.exists(class_dir):
            os.mkdir(class_dir, 0755)
        for num in range(0,99):
            device_dir = os.path.join(class_dir, base_name + str(num))
            if not os.path.exists(device_dir):
                os.mkdir(device_dir, 0755)
                self.path = device_dir
                break
        if self.path is None:
            raise Exception("Device directory '{}' not available!".format(
                os.path.join(class_dir, base_name + "<num>"))
            )

        self.add_attribute("driver_name", init=driver_name, mode="r")
        self.add_attribute("address", init=port, mode="r")
        self.add_attribute("uevent",
                           init="LEGO_DRIVER_NAME={}\nLEGO_ADDRESS={}".format(
                               driver_name, port))
        self.add_attribute("power/autosuspend_delay_ms")
        self.add_attribute("power/control", init="auto")
        self.add_attribute("power/runtime_active_time", init=0, mode="r")
        self.add_attribute("power/runtime_status", init="unsupported", mode="r")
        self.add_attribute("power/runtime_suspended_time", init=0, mode="r")

    def __del__(self):
        if self.path:
            shutil.rmtree(self.path)

    def add_attribute(self, name, init=None, mode="rw"):
        if name in self.attributes:
            raise KeyError("Attribute '{}' already exists".format(name))
        self.attributes.add(name)

        attrib_dir = os.path.join(self.path, os.path.dirname(name))
        if not os.path.exists(attrib_dir):
            os.makedirs(attrib_dir, 0755)
        attrib_file = os.path.join(self.path, name)
        with open(attrib_file, "w") as f:
            if init is not None:
                f.write(str(init))
        if mode == "rw" or mode == "wr":
            os.chmod(attrib_file, 0664)
        elif mode == "r":
            os.chmod(attrib_file, 0444)
        elif mode == "w":
            os.chmod(attrib_file, 0220)
        else:
            raise ValueError("Incorrect mode '{}'".format(mode))


class MockMotor(MockDevice):

    COMMANDS = "run-forever run-to-abs-pos run-to-rel-pos run-timed " \
               "run-direct stop reset"
    STOP_ACTIONS = "coast brake hold"

    def __init__(self, device_root_path, driver_name, port):
        MockDevice.__init__(self, device_root_path,
                            "tacho-motor", "motor", driver_name, port)
        self.add_attribute("command", mode="w")
        self.add_attribute("commands", init=MockMotor.COMMANDS, mode="r")
        self.add_attribute("count_per_rot", init=360, mode="r")
        self.add_attribute("duty_cycle", init=0, mode="r")
        self.add_attribute("duty_cycle_sp", init=0)
        self.add_attribute("encoder_polarity", init="normal")
        self.add_attribute("hold_pid/Kd")
        self.add_attribute("hold_pid/Ki")
        self.add_attribute("hold_pid/Kp")
        self.add_attribute("polarity", init="normal")
        self.add_attribute("position", init=0)
        self.add_attribute("position_sp", init=0)
        self.add_attribute("ramp_up_sp", init=0)
        self.add_attribute("ramp_down_sp", init=0)
        self.add_attribute("speed", init=0, mode="r")
        self.add_attribute("speed_pid/Kd", init=0)
        self.add_attribute("speed_pid/Ki", init=60)
        self.add_attribute("speed_pid/Kp", init=1000)
        self.add_attribute("speed_regulation", init="off")
        self.add_attribute("speed_sp", init=0)
        self.add_attribute("state", init="", mode="r")
        self.add_attribute("stop_action", init="coast")
        self.add_attribute("stop_actions", init=MockMotor.STOP_ACTIONS,mode="r")
        self.add_attribute("time_sp", init=0)


class MockMediumMotor(MockMotor):

    def __init__(self, device_root_path, port):
        MockMotor.__init__(self, device_root_path, "lego-ev3-m-motor", port)


class MockLargeMotor(MockMotor):

    def __init__(self, device_root_path, port):
        MockMotor.__init__(self, device_root_path, "lego-ev3-l-motor", port)


class MockSensor(MockDevice):

    def __init__(self, device_root_path, driver_name, port):
        MockDevice.__init__(self, device_root_path,
                            "lego-sensor", "sensor", driver_name, port)
        self.add_attribute("bin_data", init="\u0001", mode="r")
        self.add_attribute("bin_data_format", init="s8", mode="r")
        self.add_attribute("command", mode="w")
        self.add_attribute("commands", mode="r")
        self.add_attribute("decimals", init=0, mode="r")
        self.add_attribute("direct")
        self.add_attribute("fw_version", init="", mode="r")
        self.add_attribute("num_values", init=1, mode="r")
        self.add_attribute("poll_ms")
        self.add_attribute("text_value", mode="r")
        self.add_attribute("units", init="pct", mode="r")
        for n in range(0,8):
            self.add_attribute("value" + str(n), mode="r")


class MockColorSensor(MockSensor):

    def __init__(self, device_root_path, port):
        MockSensor.__init__(self, device_root_path, "lego-ev3-color", port)
        self.add_attribute("mode", init="COL-REFLECT")
        self.add_attribute("modes", init="COL-REFLECT COL-AMBIENT COL-COLOR REF-RAW RGB-RAW COL-CAL", mode="r")


class MockIrSensor(MockSensor):

    def __init__(self, device_root_path, port):
        MockSensor.__init__(self, device_root_path, "lego-ev3-ir", port)
        self.add_attribute("mode", init="IR-PROX")
        self.add_attribute("modes", init="IR-PROX IR-SEEK IR-REMOTE IR-REM-A IR-S-ALT IR-CAL", mode="r")
