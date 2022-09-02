import socketserver
import json
import datetime
import sys
import os

MESSAGE = b"""HTTP/1.1 200 OK
Content-Type: text/html

<html>
<body>
<p>(c) 2022 Enderbyte Programs</p>
<p style="color:red;">DO NOT HACK THIS SERVER PLEASE</p>
<p style="color:blue;font-size:100px;">Welcome to The Enderbyte Programs Statistics Server</p>
<p style="font-size:50px;color:green;">Have a nice day</p>
<p>Thank you for visiting :) Also here is a nice dog v</p>
<button type="button" onClick="parent.location='https://enderbyte09.wixsite.com/programs'">Visit My Main Website</button>
<img src="https://github.com/Enderbyte-Programs/webserver/raw/main/dog.jpg" alt="A dog">
</body>
</html>
"""

M404 = b"""HTTP/1.1 404 ERROR
Content-Type: text/html

<html>
<body>
<p>Error 404.</p>
</body>
</html>
"""

SERVER_IP = "216.232.200.238:10223"

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        try:
            self.data = self.request.recv(8192).strip()
            # self.request is the TCP socket connected to the client
            print(str(datetime.datetime.now()),self.client_address[0]," Connected to server")
            if not self.data == b"":
                pass
                
            else:
                print("Empty message")
                return
            # Send back a message in html
            
            try:
                vd[str(self.client_address[0])] += 1
            except:
                vd[str(self.client_address[0])] = 1
            print(len(vd),"IP addresses have connected to this server")
            with open("users.json","w+") as f:
                f.write(json.dumps(vd))
            if len(self.data) < 10000:
                with open("data.txt","a+") as g:
                    g.write(self.client_address[0])
                    g.write(" says ")
                    g.write(str(self.data))
                    g.write("\n")
            else:
                print("Server recieved packet greater than 10 KB!")
            with open("server.log","a+") as l:
                l.write(str(datetime.datetime.now()))
                l.write(" ")
                l.write(self.client_address[0])
                l.write("\n")
            #Accept Basic Utilities data
            
            if "&&BU" in str(self.data).split("$")[0].replace("b'",""):
                budata = str(self.data).split("$")
                try:
                    buver = budata[1]
                    buos = budata[2]
                except IndexError:
                    print("Invalid basic utilities string")
                else:
                    budict["lastupdated"] = str(datetime.datetime.now())
                    
                    nu = False
                    i = -1
                    if budict["ulist"]:
                        for user in budict["ulist"]:
                            i += 1
                            if user["ip"] == self.client_address[0]:
                                budict["ulist"][i]["joinlist"].append(str(datetime.datetime.now()))
                                budict["ulist"][i]["jtimes"] = len(user["joinlist"])
                                for osp in user["oses"]:
                                    if buos != osp:
                                        budict["ulist"][i]["oses"].append(buos)
                                for version in user["versions"]:
                                    if version != buver:
                                        budict["ulist"][i]["versions"].append(buver)
                                break
                            else:
                                nu = True
                    else:
                        nu = True
                    if nu:#New user setup
                        print("Setting up new user")
                        budict["ulist"].append({"ip":self.client_address[0],"joinlist":[str(datetime.datetime.now())],"jtimes":1,"oses":[buos],"versions":[buver]})
                    with open("bu.json","w+") as f:
                        f.write(json.dumps(budict))
            else:
                
                self.apidat = self.data.split(b" ")[1].decode("utf-8")
                print(self.apidat)
                if self.apidat == "/":
                    self.request.sendall(MESSAGE)
                elif self.apidat == "/favicon.ico":
                    with open("favicon.ico","rb") as r:
                        self.request.sendall(r.read())
                elif self.apidat == "/download":
                    MSG = """HTTP/1.1 200 OK
Content-Type: text/html

<html>
<style>
table, th, td {
  border:1px solid black;
}
</style>
<body>
<p>To download a file here, click a link in the table. If applicable, confirm the download in your browser</p>
<table>
<tr>
<th>File Name</th>
<th>Size (Kilobytes)</th>
</tr>
$$DATA
<table>
</body>
</html>"""
                    print("Loading archives")
                    fs = ['<td><a href='+f'/download/{fl}'+">"+str(fl) +"</a></td>" for fl in os.listdir(os.getcwd()+"/archives")]
                    
                    sz = []
                    szx = [os.path.getsize(os.getcwd() + "/archives/"+ path)/1000 for path in os.listdir(os.getcwd()+"/archives")]
                    print("Loading sizes")
                    for size in szx:
                        sz.append("<td>"+str(size)+"</td>")
                    LDATA = ""
                    for i in range(0,len(fs)-1):
                        LDATA += f"<tr>{fs[i]}{sz[i]}</tr>"
                    MSG = MSG.replace("$$DATA",LDATA)
                    print("sending")
                    self.request.sendall(MSG.encode("utf-8"))

                elif "/download/" in self.apidat:
                    reqfile = self.apidat.split("/")[-1]
                    if os.path.isfile(os.getcwd() + "/archives/" + reqfile):
                        with open(os.getcwd() + "/archives/" + reqfile,"rb") as l:
                            self.request.sendall(b"HTTP/1.0 200 ok\r\nContent-type: application/octet-stream\r\n\r\n")
                            self.request.sendall(l.read())
                    else:
                        self.request.sendall(M404)

                else:
                    self.request.sendall(M404)
        except Exception as e:
            print(str(e))
            self.request.sendall(f"""
HTTP/1.1 400 ERROR
Content-Type: text/html

<html>
<body>
<p>Critical Server Error {e}</p>
</body>
</html>
""".encode("utf-8"))

if __name__ == "__main__":
    HOST, PORT = "192.168.1.170", 10223
    try:
        with open("users.json") as f:
            vd = json.load(f)
    except:
        vd = {}
    try:
        with open("bu.json") as f:
            budict = json.load(f)
            
    except:
        budict = {"ulist":[]}
    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    def he(type,value,traceback):
        server.shutdown()
        sys.exit(1)
    sys.excepthook = he
    print("Server is online")
    server.serve_forever()
