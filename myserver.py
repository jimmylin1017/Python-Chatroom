import socket, select, sys, time

class MyServer():

    clientSocketList = list() # store all client socket
    clientSocketName = dict() # socket -> name
    clientSocketMap = dict() # name -> socket
    
    bufferSize = 1024 # use for receive buffer

    def __init__(self, serverPort, clientSocketLimit = 5):
        self.serverPort = serverPort
        self.clientSocketLimit = clientSocketLimit
    
    def Create(self):
        try:
            self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.serverSocket.bind(('0.0.0.0', self.serverPort)) # bind with any ip address by '0.0.0.0'
        except socket.error as e:
            print("server socket create failed : %s" % e)

    def Listen(self):
        try:
            self.serverSocket.listen(self.clientSocketLimit)
        except socket.error as e:
            print("server socket listen failed : %s" % e)

    # convert message to utf-8 and send to target client
    # clientSocket: target client fd
    # message: string
    def SendMessage(self, clientSocket, message):
        data = message.encode('UTF-8')
        clientSocket.send(data)
        print("SendMessage : ", message)

    def BroadCast(self, message):
        data = message.encode('UTF-8')
        for clientSocket in self.clientSocketList:
            clientSocket.send(data)
        print("BroadCast : ", message)

    # send message to target client
    # sock: source client fd
    # targetName: string for target client name
    # message: string
    def UniCast(self, sock, targetName, message):
        if targetName in self.clientSocketMap.keys():
            message = "[" + self.clientSocketName[sock] + " -> " + targetName + "] : " + message
            self.SendMessage(self.clientSocketMap[targetName], message)
            self.SendMessage(sock, message)
        else:
            self.SendMessage(sock, targetName + " is not exist!")

    # get client name from client
    # sock: source client fd
    def Login(self, sock, name):
        if name in self.clientSocketMap.keys():
            self.SendMessage(sock, name + " can not be used!")
        else:
            self.clientSocketName[sock] = name
            self.clientSocketMap[name] = sock
            self.SendMessage(sock, name)
            time.sleep(0.1)
            self.BroadCast("<client %s login>" % self.clientSocketName[sock])

    # delete client information
    # sock: source client fd
    def Logout(self, sock):
        self.SendMessage(sock, "/logout")
        tempName = self.clientSocketName[sock]
        # delete all client information
        self.clientSocketList.remove(sock)
        del self.clientSocketMap[self.clientSocketName[sock]]
        del self.clientSocketName[sock]
        self.BroadCast("<client %s is logout>" % tempName)

    # if client disconnect unexpexted, delete client information
    # sock: source client fd
    def DisConnect(self, sock):
        tempName = self.clientSocketName[sock]
        # delete all client information
        self.clientSocketList.remove(sock)
        del self.clientSocketMap[self.clientSocketName[sock]]
        del self.clientSocketName[sock]
        self.BroadCast("<client %s is disconnect>" % tempName)

        

    def Start(self):
        self.Create()
        self.Listen()

        print("Listing...")

        # use select to choose which client need to be read
        while 1:
            try:
                readable, _, _ = select.select(self.clientSocketList + [self.serverSocket], [], [])
            except select.error as e:
                print("select failed : %s" % e)

            for sock in readable:
                if sock is self.serverSocket: # have new client which want to connect with server
                    try:
                        clientSocket, clientAddress = self.serverSocket.accept()
                        self.clientSocketList.append(clientSocket)
                        print("client address %s" % str(clientAddress))
                    except socket.error as e:
                        print("server socket accept failed : %s" % e)
                else: # client have new message to be read
                    try:
                        data = sock.recv(self.bufferSize)
                        if data:
                            message = data.decode('UTF-8')
                            message = message.split()
                            print("receive : ", message)
                            if message[0] == "/name":
                                self.Login(sock, message[1])
                            elif message[0] == "/logout":
                                self.Logout(sock) 
                            elif message[0] == "/chat":
                                self.UniCast(sock, message[1], message[2])
                            else:
                                self.BroadCast(self.clientSocketName[sock] + " : " + message[0])
                    except socket.error as e:
                        print("server socket receive failed : %s" % e)
                        self.DisConnect(sock)
