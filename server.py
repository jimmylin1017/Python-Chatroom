import socket, select, sys
import myserver

if __name__=='__main__':

    serverPort = 6666
    clientSocketLimit = 5

    mainServer = myserver.MyServer(serverPort, clientSocketLimit)

    mainServer.Start()



            
       
    
