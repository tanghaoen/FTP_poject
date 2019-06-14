import socketserver
import optparse
import os, sys

Path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Path)
from conf import settings
from core import mysever


class Argvhandler():
    def __init__(self):
        self.op = optparse.OptionParser()
        self.op.add_option("-s", "--s", dest="sever")
        self.op.add_option("-p", "--port", dest="post")
        options, args = self.op.parse_args()

        self.verify_args(options, args)

    def start(self):
        print("the sever is working")
        s = socketserver.ThreadingTCPServer((settings.ip, settings.port),mysever.MySever)
        s.serve_forever()

    def verify_args(self, options, args):
        cmd = args[0]

        if hasattr(self, cmd):
            func = getattr(self,cmd)
            func()




