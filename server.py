import http.server
import json
import datetime
import sys
import os
import shlex

SERVER_IP = "216.232.200.238:10223"
def retrievedasp(name,code,retrconlen=True):
    with open(os.getcwd()+"/assets/"+name,"r") as f:
        body = f.read()
    data = "HTTP/1.1 "
    data += f"{code} "
    if str(code)[0] != "2":
        data += "ERROR"
    else:
        data += "OK"
    data += "\nContent-type: text/html\n"
    if retrconlen:
        data += f"Content-length: {len(body)}\n\n"
    else:
        data += "\n"
    data += body
    return data
        
class MyTCPHandler(http.server.BaseHTTPRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        global ACCOUNTS
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
                    g.write(str(datetime.datetime.now()).replace(" ","_") + " ")
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
            elif "msgs" in str(self.data):
                try:
                    print(str(self.data).replace("\'",""))
                    msdata = shlex.split(str(self.data).replace("\'",""))
                    print(msdata)
                    if msdata[1] == "newacc":
                        if msdata[2] in ACCOUNTS.keys():
                             #Account already exists
                            self.request.sendall(b"ERROR 800")
                        else:
                            ACCOUNTS[msdata[2]] = {}
                            ACCOUNTS[msdata[2]]["pwd"] = msdata[3]
                            ACCOUNTS[msdata[2]]["activeip"] = self.client_address[0]#This will be updated with new logins
                            ACCOUNTS[msdata[2]]["loggedin"] = False
                            self.request.sendall(b"OK 200")
                            with open("accounts.json","w+") as f:
                                f.write(json.dumps(ACCOUNTS))
                    elif msdata[1] == "login":
                        if msdata[2] in ACCOUNTS.keys():
                            if ACCOUNTS[msdata[2]]["pwd"] == msdata[3]:
                                ACCOUNTS[msdata[2]]["activeip"] = self.client_address[0]#This will be updated with new logins
                                ACCOUNTS[msdata[2]]["loggedin"] = True
                                with open("accounts.json","w+") as f:
                                    f.write(json.dumps(ACCOUNTS))
                                self.request.sendall(b"OK 200")
                            else:
                                self.request.sendall(b"ERROR 802")#Wrong password
                        else:
                            self.request.sendall(b"ERROR 801")#Account not found
                    elif msdata[1] == "logoff":
                        if msdata[2] in ACCOUNTS.keys():
                            if ACCOUNTS[msdata[2]]["pwd"] == msdata[3]:
                                ACCOUNTS[msdata[2]]["loggedin"] = False
                                self.request.sendall(b"OK 200")
                            else:
                                self.request.sendall(b"ERROR 802")#Wrong password
                        else:
                            self.request.sendall(b"ERROR 801")#Account not found
                    elif msdata[1] == "send":
                        acsendname = self.client_address[0]
                        for ac in ACCOUNTS.keys():
                            if ACCOUNTS[ac]["activeip"] == self.client_address[0] and ACCOUNTS[ac]["loggedin"]:
                                acsendname = ac
                                break
                        msdata = [m.replace("\\n","\n") for m in msdata]
                        MESSAGES.append(f'({datetime.datetime.now()}) [{acsendname}] {" ".join(msdata[2:])}')
                        with open("messages.txt","w+") as f:
                            f.write("\n".join(MESSAGES))
                except Exception as e:
                     self.request.sendall(f"ERROR 805 {str(e)}".encode("utf-8"))
            else:
                
                self.apidat = self.data.split(b" ")[1].decode("utf-8")
                print(self.apidat)
                if self.apidat == "/":
                    with open("server.log") as lf:
                        ucall = len(lf.readlines())
                    self.request.sendall(retrievedasp("home.html",200).replace("$V",str(ucall)).encode("utf-8"))
                elif self.apidat == "/favicon.ico":
                    with open("favicon.ico","rb") as r:
                        self.request.sendall(r.read())
                elif self.apidat == "/download":
                    MSG = retrievedasp("downloads.html",200,False)
                    fs = ['<td><a href='+f'/download/{fl}'+">"+str(fl) +"</a></td>" for fl in os.listdir(os.getcwd()+"/archives")]
                    
                    sz = []
                    szx = [os.path.getsize(os.getcwd() + "/archives/"+ path)/1000 for path in os.listdir(os.getcwd()+"/archives")]
                    for size in szx:
                        sz.append("<td>"+str(size)+"</td>")
                    LDATA = ""
                    for i in range(0,len(fs)-1):
                        LDATA += f"<tr>{fs[i]}{sz[i]}</tr>"
                    MSG = MSG.replace("$$DATA",LDATA)
                    self.request.sendall(MSG.encode("utf-8"))
                elif self.apidat == "/messages":
                    ucl = ""
                    for message in MESSAGES:
                        ucl += f"<p>{message}</p>\n"
                    mdata = retrievedasp("msg.html",200,False)
                    self.request.sendall(mdata.replace("$DATA",ucl).encode("utf-8"))
                elif self.apidat == "/messages/send":
                    raise NotImplementedError("NOT YET")
                elif "/messages/send/" in self.apidat:
                    MESSAGES.append(f"({datetime.datetime.now()}) [{self.client_address[0]}] {'/'.join(self.apidat.split('/')[3:])}")
                    with open("messages.txt","w+") as f:
                        f.write("\n".join(MESSAGES))
                    self.request.sendall(retrievedasp("msgconf.html",200,True).encode("utf-8"))
                elif "/download/" in self.apidat:
                    reqfile = self.apidat.split("/")[-1]
                    if os.path.isfile(os.getcwd() + "/archives/" + reqfile):
                        with open(os.getcwd() + "/archives/" + reqfile,"rb") as l:
                            rsdata = l.read()
                            self.request.sendall(f"HTTP/1.1 200 OK\r\nContent-type: application/octet-stream\r\nContent-length: {len(rsdata)}\r\n\r\n".encode("utf-8"))
                            self.request.sendall(rsdata)
                    else:
                        raise FileNotFoundError(f"Failed to find file {reqfile}")

                else:
                    self.request.sendall(retrievedasp("404.html",404).encode("utf-8"))
        except Exception as e:
            print(str(e))
            self.request.sendall(f"""
HTTP/1.1 400 ERROR
Content-Type: text/html

<html>
<head>
<title>Critical Server Error</title>
</head>
<body>
<h1>Critical Server Error</h1>
<p>{e}</p>
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
    with open("accounts.json") as f:
        ACCOUNTS = json.load(f)
    with open("messages.txt") as f:
        MESSAGES = f.readlines()

    # Create the server, binding to localhost on port 9999
    server = http.server.ThreadingHTTPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    def he(type,value,traceback):
        server.shutdown()
        sys.exit(1)
    sys.excepthook = he
    print("Server is online")
    server.serve_forever()
