import socket, select, sys
import myclient
import threading

if __name__ == '__main__':
    
    serverPort = 6666
    serverHost = '127.0.0.1'

    mainClient = myclient.MyClient()
    mainClient.Start(serverHost, serverPort)
    