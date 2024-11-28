import telnetlib
import sys
import time


class Gantry:
    def __init__(self, excl_ip, excl_port):
        self.excl_ip = excl_ip
        self.excl_port = excl_port

    def initialize(self):
        self.tn_client = telnetlib.Telnet(self.excl_ip, self.excl_port)

    def move_from_to(self, x, y):
        pass
