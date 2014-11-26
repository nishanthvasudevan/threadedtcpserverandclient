#!/usr/bin/python

import socket
import sys

HOST = 'localhost'
#PORT = 50006
query=sys.argv[1]
port = sys.argv[2]
PORT = int(port)

try:
  	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
  	sys.stderr.write("[ERROR] %s\n" % msg[1])
  	sys.exit(1)

try:
  	sock.connect((HOST, PORT))
except socket.error, msg:
  	sys.stderr.write("[ERROR] %s\n" % msg[1])
  	sys.exit(2)

stream="%s" % (query)
sock.send(stream)
#data = sock.recv(1024)
#print data
#string = ""
while 1:
  	#string = string + data
  	data = sock.recv(8192)
	if not data:break
	sys.stdout.write(data)
sock.close()

#print string
sys.exit(0)
