import socket
import threading
import struct
import string
import pdb
import atexit
import sys, time
from daemon import Daemon
from os import fork, chdir, setsid, umask
from sys import exit
import logging

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
handler = logging.FileHandler('/var/log/server.log')
handler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)

class clientThread(threading.Thread):     
    def __init__(self, serv):
        threading.Thread.__init__(self)
        self.server = serv
        self.clientList = []
        self.running = True
        logger.info("Client thread created. . .")
    def run(self):
        logger.info("Beginning client thread loop. . .")
        while self.running:
                for client in self.clientList:
                    try:
                        fileName = client.sock.recv(self.server.BUFFSIZE)
                        result = client.sendBlockSize(fileName)
                        if (result == 1):
                            client.sendFile(fileName)
                        else:
                            logger.info("Could find file...")
                            self.clientList.remove(client)
                    except Exception, e:
                        pass
                                                                    
class clientObject(object):
    def __init__(self,clientInfo):
        self.sock = clientInfo[0]
        self.address = clientInfo[1]

    def update(self,message):
        self.sock.send(message)

    def sendFileName(self, fileName):
        self.sock.send(fileName)

    def sendBlockSize(self, fileName):
        try:
            fileName = fileName[:-1]
            f = open(fileName)
            lines = f.readlines()
            f.close()
            noOfLines = len(lines)
            self.sock.send(str(noOfLines))
            logger.info("Sending blockSize...")
            return 1
        except Exception, e:
            self.sock.send("Wrong file name " + fileName)
            return 0

    def sendFile(self, fileName):
        logger.info("Sending file " + fileName)
        fileName = fileName[:-1]
        f = open(fileName)
        lines = f.readlines()
        f.close()
        for i in range(0, len(lines)):
            self.sock.send(lines[i])
        self.sock.close()          

class Server(Daemon):
    def __init__(self):
        self.HOST = "0.0.0.0"
        self.PORT = 22085
        self.BUFFSIZE = 1024
        self.ADDRESS = (self.HOST,self.PORT)
        self.clientList = []
        #a = raw_input("Press enter to start the server. . .")
        self.running = True
        self.serverSock = socket.socket()
        self.serverSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSock.bind(self.ADDRESS)
        self.serverSock.listen(2)
        self.clientThread = clientThread(self)
        #print("Starting client thread. . .")
        self.clientThread.start()
        #print("Awaiting connections. . .")
        while self.running:
            clientInfo = self.serverSock.accept()
            logger.info("Client connected from {}.".format(clientInfo[1]))
            self.clientThread.clientList.append(clientObject(clientInfo))

        self.serverSock.close()
        print("- end -") 

# Dual fork hack to make process run as a daemon
if __name__ == "__main__":
	try:
		pid = fork()
		if pid > 0:
			exit(0)
	except OSError, e:
		exit(1)

	#chdir("/")
	setsid()
	umask(0)

	try:
		pid = fork()
		if pid > 0:
			exit(0)
	except OSError, e:
		exit(1)

	serv = Server()
