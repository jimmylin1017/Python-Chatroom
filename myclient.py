import socket, select
import threading

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
                        print(message)
                        if clientName == message:
                            break
                except socket.error as e:
                    print("client socket receive failed : %s" % e)

    def SendMessage(self, message):
        data = message.encode('UTF-8')
        try:
            self.serverSocket.send(data)
            print("SendMessage : ", message)
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
                            message = data.decode('UTF-8')
                            print(message)
                            if message == "/logout":
                                self.checkLogin = False
                                exit()
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
                if(message):
                    self.SendMessage(message)
            except KeyboardInterrupt as e:
                print("KeyboardInterrupt : %s" % e)
                self.SendMessage("/logout")
