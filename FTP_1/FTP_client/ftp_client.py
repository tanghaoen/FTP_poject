import optparse
from socket import *
import configparser
import json
import os, sys

s_code = {
    250: "invalid cmd format, e.g: {'action':'get','filename':'text.py','size':344}",
    251: "invalid cmd",
    252: "invalid auth data",
    253: "wrong username or password",
    254: "passed authentication",
    255: "filename doesn't provided",
    256: "file doesn't exist on server",
    257: "ready to send file",
    258: "md5 verification",

    800: "the file exist but not enough, is countinue",
    801: "the flie exist!",
    802: "ready to receive datas",

    900: "md5 valdate  success"

}


class clienthandle():
    def __init__(self):
        self.op = optparse.OptionParser()

        self.op.add_option("-s", "--server", dest="server")
        self.op.add_option("-P", "--port", dest="port")
        self.op.add_option("-u", "--username", dest="username")
        self.op.add_option("-r", "--password", dest="password")
        self.options, self.args = self.op.parse_args()

        self.verify_args(self.options, self.args)
        self.make_connection()
        self.mainpath = os.path.dirname(os.path.abspath(__file__))
        self.c = 0

    def verify_args(self, options, args):
        server = options.server
        port = options.port
        username = options.username
        password = options.password
        if int(port) > 0 and int(port) < 65535:
            return True
        else:
            exit("the port is 0-65535")

    def make_connection(self):
        self.sock = socket()
        self.sock.connect((self.options.server, int(self.options.port)))

    def user(self):
        o = input("Do you have an account[Y/N]").strip()
        if o == "N":
            username = input("Please enter the username you want to register:").strip()
            password = input("Please enter the password you want to register:").strip()
            print(type(username), type(password))
            data = {
                "action": "register",
                "username": username,
                "password": password
            }
            self.sock.send(json.dumps(data).encode("utf-8"))
            h = self.sock.recv(1024).decode("utf-8")
            return self.get_authresult(username, password)

        else:
            if self.options.username is None or self.options.password is None:
                username = input("请从新输入username: ")
                password = input("请从新输入password: ")
                return self.get_authresult(username, password)

            return self.get_authresult(self.options.username, self.options.password)

    def receive_information(self):
        data = self.sock.recv(1024).decode("utf-8")
        data = json.loads(data)
        return data

    def get_authresult(self, use, pwd):
        data = {
            "action": "auth",
            "username": use,
            "password": pwd
        }
        self.sock.send(json.dumps(data).encode("utf-8"))
        re = self.receive_information()
        print(re["s_code"])
        if re["s_code"] == 254:
            self.cur = use
            print(s_code[254])
            return True
        else:
            print(s_code[re["s_code"]])

    def mutual(self):
        if self.user():
            print("begin mutual...")
        while True:
            info = input("[%s]" % self.cur).strip()
            in_list = info.split()
            if len(in_list) == 0: continue
            in_list = info.split()
            if hasattr(self, in_list[0]):
                func = getattr(self, in_list[0])
                func(*in_list)
            else:
                print("Invalid cmd")

    def put(self, *in_list):

        action, locapath, targerpath = in_list
        locapath = os.path.join(self.mainpath, locapath)
        file_name = os.path.basename(locapath)
        file_size = os.stat(locapath).st_size
        data = {
            "action": "put",
            "file_name": file_name,
            "file_size": file_size,
            "targerpath": targerpath
        }
        self.sock.send(json.dumps(data).encode("utf-8"))
        is_exist = self.sock.recv(1024).decode("utf-8")

        has_sent = 0
        if is_exist == "800":
            urse_choice = input("the file exist,but not enough,is countinue?[Y/N]").strip()
            if urse_choice.upper() == "Y":
                self.sock.sendall("Y".encode("utf-8"))
                countion_posittion = self.sock.recv(1024).decode("utf-8")
                has_sent += int(countion_posittion)
            else:
                self.sock.sendall("N".encode("utf-8"))

        elif is_exist == "801":
            print("the file exiting")
            return
        a = open(locapath, "rb")
        while has_sent < file_size:
            data = a.read(1024)
            self.sock.sendall(data)
            has_sent += len(data)
            self.show_progress(has_sent, file_size)

        a.close()
        print("succeed!!!")

    def download(self, *in_list):
        big = 0
        data = {
            "action": "download",
            "dirname": in_list[1]
        }
        self.sock.sendall(json.dumps(data).encode("utf-8"))
        file_size = int(self.sock.recv(1024).decode("utf-8"))
        k = os.path.join(self.mainpath, "download1", in_list[1])
        big = 0
        if os.path.exists(k):
            has_size = os.stat(k).st_size
            if has_size < file_size:
                self.sock.sendall("800".encode("utf-8"))
                a = self.sock.recv(1024).decode("utf-8")
                print(a)
                answer = input("Please select a:").strip()
                self.sock.sendall(answer.encode("utf-8"))
                if answer == "Y":
                    self.sock.sendall(str(has_size).encode("utf-8"))
                    big += has_size
                    f = open(k, "ab")
                else:
                    f = open(k, "wb")
            else:
                self.sock.sendall("801".encode("utf-8"))
                return
        else:
            self.sock.sendall("802".encode("utf-8"))
            f = open(k, "wb")
        while big < file_size:
            try:
                data = self.sock.recv(1024)

            except Exception as e:
                break
            f.write(data)
            big += len(data)
            self.show_progress(big, file_size)

        print("succeed!!!")

    def show_progress(self, has, total):
        rate = float(has) / float(total)
        rate_num = int(rate * 100)

        if self.c != rate_num:
            sys.stdout.write("%s%% %s\r" % (rate_num, "*" * rate_num))
        self.c = rate_num

    def Is(self, *in_list):
        data = {
            "action": "Is",
        }
        self.sock.sendall(json.dumps(data).encode("utf-8"))
        data = self.sock.recv(1024).decode("utf-8")
        print(data)

    def cd(self, *in_list):
        data = {
            "action": "cd",
            "dirname": in_list[1]

        }
        self.sock.sendall(json.dumps(data).encode("utf-8"))
        data = self.sock.recv(1024).decode("utf-8")
        self.cur = os.path.basename(data)

    def mkdir(self, *in_list):
        data = {
            "action": "mkdir",
            "dirname": in_list[1]
        }
        self.sock.sendall(json.dumps(data).encode("utf-8"))
        data = self.sock.recv(1024).decode("utf-8")


ch = clienthandle()
ch.mutual()
