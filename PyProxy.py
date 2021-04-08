#!/usr/bin/env python3

import socket
from PyNetTools.PyNetTools import *
from PyPrintSystem.PyPrintSystem import *
from sys import argv
from hashlib import md5

verbose = False
loop = True
lastHost = "0.0.0.0"

if len(argv) == 1:
    p("Usage: " + argv[0] + " <(t)rue/)f)alse>", 'e', verbose)
    exit(1)
else:
    if argv[1].lower() in ("true", 't'):
        verbose = True
    elif argv[1].lower() in ("false", 'f'):
        verbose = False
    else:
        p("Usage: " + argv[0] + " <(t)rue/(f)alse>", 'e', verbose)
        exit(2)

p("Starting proxy...", 'i', verbose)

p("Initializing socket...", 'v', verbose)
proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

p("Binding to " + getPrivateIP() + ":8080...", 'v', verbose)
proxySocket.bind((getPrivateIP(), 8080))

p("Listening for connections...", 'v', verbose)
proxySocket.listen(5)

while loop:
    clientSocket, address = proxySocket.accept()
    if lastHost != address[0]:
        p("Got connection from: " + address[0] + ":" + str(address[1]), 's', verbose)
        lastHost = address[0]
    
    clientData = clientSocket.recv(4096)

    if clientData:
        rawClientData = clientData
        clientData = clientData.splitlines()
        for clientDataLine in clientData:
            clientDataLine = clientDataLine.decode("utf-8")
            
            if clientDataLine.startswith("CONNECT "):
                remoteHost = clientDataLine.split(' ')[1].strip().split(':')[0]
                remotePort = clientDataLine.split(' ')[1].strip().split(':')[1]

                p("Forwarding data (" + remoteHost + ':' + remotePort + ")->(" + md5(rawClientData).hexdigest() + ")", 'v', verbose)

                serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                serverSocket.connect((remoteHost, int(remotePort)))
                serverSocket.send(rawClientData)
                serverSocket.settimeout(2)
                serverData = serverSocket.recv(4096)

                p("Receiveing data (" + remoteHost + ':' + remotePort + ")<-(" + md5(serverData).hexdigest() + ")", 'v', verbose)

                clientSocket.send(serverData)
                clientSocket.close()

    clientSocket.close()

doHeart("Thank you", 4)
