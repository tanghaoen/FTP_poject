import socketserver
import json
import configparser
import os, sys

Path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(Path)
from conf import settings
import os

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


class MySever(socketserver.BaseRequestHandler):
    def handle(self):
        # print("conn is", self.request)
        # print("addr is:", self.client_address)
        while True:
            try:

                data = self.request.recv(1024).strip()
                print("data-----", data)
                if len(data) == 0: break

                data = json.loads(data.decode("utf-8"))
                print("data:", type(data))

                if data.get("action"):
                    print(str(data.get("action")))
                    if hasattr(self, "%s" % data.get("action")):
                        func = getattr(self, data.get("action"))
                        func(**data)
                    else:
                        print("Invalid cmd")
                        self.send_answer(251)
                else:
                    print("Invalid cmd")
                    self.send_answer(250)

                # self.request.sendall(a.encode("utf-8"))
            except Exception as e:
                print(e)
                break

    def send_answer(self, s_code):
        answer = {"s_code": s_code}
        self.request.sendall(json.dumps(answer).encode("utf-8"))

    def auth(self, **data):
        username = data["username"]
        password = data["password"]
        urse = self.jude(username, password)
        if urse:
            self.send_answer(254)
        else:
            self.send_answer(253)

    def jude(self, urse, pwd):
        cfg = configparser.ConfigParser()
        cfg.read(settings.ACCOUNT_PATH)
        if urse in cfg.sections():

            if cfg[urse]["password"] == pwd:
                self.ures = urse
                self.mainpath = os.path.join(settings.BASE_DIR, "home", self.ures)
                print("weclcome")
                return urse

    def put(self, **data):
        print("data", type(data))
        file_name = data.get("file_name")
        file_size = data.get("file_size")
        targerpath = data.get("targerpath")

        abs_path = os.path.join(self.mainpath, targerpath, file_name)

        big = 0

        if os.path.exists(abs_path):
            has_size = os.stat(abs_path).st_size
            if has_size < file_size:
                self.request.sendall("800".encode("utf-8"))
                choise = self.request.recv(1024).decode("utf-8")
                if choise == "Y":
                    self.request.sendall(str(has_size).encode("utf-8"))
                    big += has_size
                    f = open(abs_path, "ab")

                else:
                    f = open(abs_path, "wb")
            else:
                self.request.sendall("801".encode("utf-8"))
                return
        else:
            self.request.sendall("802".encode("utf-8"))
            f = open(abs_path, "wb")

        while big < file_size:
            try:
                data = self.request.recv(1024)

            except Exception as e:
                break
            f.write(data)
            big += len(data)
        f.close()

    def Is(self, **data):
        g_file = os.listdir(self.mainpath)
        file_str = "\n".join(g_file)
        if not len(g_file):
            file_str = "<empty dit>"
        self.request.sendall(file_str.encode("utf-8"))
        return

    def cd(self, **data):

        dirname = data.get("dirname")
        if dirname == "..":
            self.mainpath = os.path.dirname(self.mainpath)
        else:
            self.mainpath = os.path.join(self.mainpath, dirname)
        self.request.sendall(self.mainpath.encode("utf-8"))

    def download(self, **data):
        dirname = data.get("dirname")
        download_file = os.path.join(self.mainpath, dirname)
        file_size = os.stat(download_file).st_size
        self.request.sendall(str(file_size).encode("utf-8"))
        is_exist = self.request.recv(1024).decode("utf-8")

        has_sent = 0

        if is_exist == "800":
            self.request.sendall("the file exist,but not enough,is countinue?[Y/N]".encode("utf-8"))
            answer = self.request.recv(1024).decode("utf-8")
            if answer == "Y":
                print("ssssss")
                v = self.request.recv(1024).decode("utf-8")
                print(v)
                has_sent += int(v)
                print(has_sent)
            else:
                self.request.sendall("N".encode("utf-8"))
        elif is_exist == "801":
            return
        a = open(download_file, "rb")
        while has_sent < file_size:
            data = a.read(1024)
            self.request.sendall(data)
            has_sent += len(data)
        a.close()

    def mkdir(self, **data):
        dirname = data.get("dirname")
        path = os.path.join(self.mainpath, dirname)
        if not os.path.exists(path):
            if "/" in dirname:
                os.makedirs(path)
            else:
                os.mkdir(path)

            self.request.sendall("dirname exist".encode("utf-8"))
        else:
            self.request.sendall("dirname exist".encode("utf-8"))

    def register(self, **data):
        username = data.get("username")
        password = data.get("password")
        cfg = configparser.ConfigParser()
        cfg.read(settings.ACCOUNT_PATH)
        print(username, password, type(username), type(password))
        cfg[username] = {}
        cfg[username]["password"] = password
        cfg[username]["quotation"] = "100"

        with open(settings.ACCOUNT_PATH, "w") as f:
            cfg.write(f)
        path = os.path.join(settings.BASE_DIR, "home", username)
        os.mkdir(path)

        self.request.sendall("Account setup successful please continue other operations".encode("utf-8"))


if __name__ == "__main__":
    s = socketserver.ThreadingTCPServer(("127.0.0.1", 8000), MySever)
    s.serve_forever()
