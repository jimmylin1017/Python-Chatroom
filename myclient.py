import socket, select, time, os
import threading

#display color content
RED = "\x1b[;31;1m"
BLU = "\x1b[;34;1m"
YEL = "\x1b[;33;1m"
GRE = "\x1b[;32;1m"
RESET = "\x1b[0;m"

class MyClient():

    def __init__(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.checkLogin = False
    
    def Connect(self, serverHost, serverPort):
        try:
            self.serverSocket.connect((serverHost, serverPort))
            self.checkLogin = True
        except socket.error as e:
            print("client socket connect failed : %s" % e)

    def Login(self):
        while 1:
            clientName = input("Please input username : ")
            if(clientName):
                self.SendMessage("/name " + clientName)
                try:
                    data = self.serverSocket.recv(1024)
                    if data:
                        message = data.decode('UTF-8')
                        if clientName == message:
                            break
                except socket.error as e:
                    print("client socket receive failed : %s" % e)

    def SendMessage(self, message):
        data = message.encode('UTF-8')
        try:
            self.serverSocket.send(data)
        except socket.error as e:
            print("client socket send failed : %s" % e)
    
    def UpFile(self, fileName):
        fileName=fileName
        data='/up '+fileName
        data = data.encode('UTF-8')
        try:
            self.serverSocket.send(data)
            time.sleep(0.1)
            print(GRE+"SendFile : ", fileName,RESET)
            file = open (fileName, "rb")
            data = file.read(1024)
            while (data):
                self.serverSocket.send(data)
                data = file.read(1024)
            file.close()
            time.sleep(0.1)
            data='/upf'
            data = data.encode('UTF-8')
            self.serverSocket.send(data)
            print(GRE+"SendFile finish",RESET)
        except socket.error as e:
            print("client socket send failed : %s" % e)

    def DownFile(self, fileName):
        fileName=fileName
        data='/down '+fileName
        data = data.encode('UTF-8')
        try:
            self.serverSocket.send(data)
            print(GRE+"DownFile : ", fileName,RESET)
        except socket.error as e:
            print("client socket send failed : %s" % e)

    def displayMessage(self):
        while 1:
            try:
                readable, _, _ = select.select([self.serverSocket], [], [])
            except select.error as e:
                print("select failed : %s" % e)
            for sock in readable:
                if sock is self.serverSocket:
                    try:
                        data = sock.recv(1024)
                        if data:
                            message = data.decode('utf-8', 'ignore')
                            if message[0]!='/':
                                if message[0]=='[':
                                    print(BLU+message+RESET)
                                elif message[0]=='<':
                                    print(YEL+message+RESET)
                                else:
                                    print(message)
                            if message == "/logout":
                                self.checkLogin = False
                                exit()
                            message = message.split()
                            if message[0]== "/down" :
                                file = open(message[1],'wb') #open in binary
                                data = sock.recv(1024)
                                while (data):
                                    if data.decode('utf-8', 'ignore')=='/downf':
                                        break;
                                    file.write(data)
                                    data = sock.recv(1024)
                                file.close()
                                print(GRE+"GetFile : %s finish %s" %(message[1] , RESET))
                    except socket.error as e:
                        print("client socket receive failed : %s" % e)
                        self.checkLogin = False
                        print("Server Shutdown")
                        exit()
        
    def Start(self, serverHost, serverPort):
        self.Connect(serverHost, serverPort)
        self.Login()
        try:
            thread = threading.Thread(target = self.displayMessage, args = ())
            thread.start()
        except:
            print("Error: unable to start thread")
        while self.checkLogin:
            try:
                message = input()
                if message !='':
                    messages = message.split()
                    if messages[0]== "/up" :
                        self.UpFile(messages[1])
                    elif messages[0]== "/down" :
                        self.DownFile(messages[1])
                    else:
                        if(message):
                            self.SendMessage(message)
            except KeyboardInterrupt as e:
                print("KeyboardInterrupt : %s" % e)
                self.SendMessage("/logout")
