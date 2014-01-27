import socket
import string
import sys
import pdb

## conver string to integer
def convertNum(s):
	try:
    		return int(s)
	except ValueError:
    		return 0

host = sys.argv[1]
filename = sys.argv[2]

print host
print filename


#for i in xrange(1, total):
#	a += str(sys.argv[i])

address = (host,22085)
mySocket = socket.socket()

mySocket.connect(address)
print("Connected successfully!")

# send fileName
mySocket.send(filename)

print "Requested file : " + filename

cont = False
blockSize = mySocket.recv(1024)

if convertNum(blockSize) != 0:
	print "Received blockSize:", blockSize
	blockSize = convertNum(blockSize)
	cont = True
else:
	print blockSize
	cont = False

if cont:
	data = []
	for x in xrange(0, blockSize):
		data.append(mySocket.recv(1024))

	print "File received and saved to ", filename
	mySocket.close()

	file = open(filename, "wr")
	for i in range(0, blockSize):
		file.write(data[i])
	file.close()
else:
	pass
	
