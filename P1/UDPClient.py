from socket import *
import hashlib
import pickle
import sys
import os
import math
import time


serverName="rt3"
serverPort=10000
serverAddress = (serverName, serverPort)

#create client socket
clientSocket = socket(AF_INET,SOCK_DGRAM)
clientSocket.settimeout(0.001)

#initializes window variables (upper and lower window bounds, position of next seq number)
base=1
nextSeqnum=1
windowSize=7
window = []

#SENDS DATA
data = []
for i in range(1000):
	data.append(i);

done = False
lastackreceived = time.time()
iterator = 0


while not done or window:
#	check if the window is full	or EOF has reached
	if(nextSeqnum<base+windowSize) and not done:
#		create packet(seqnum,data,checksum)
		sndpkt = []
		sndpkt.append(nextSeqnum)
		sndpkt.append(data[iterator] + 1)
		h = hashlib.md5()
		h.update(pickle.dumps(sndpkt))
		sndpkt.append(h.digest())
#		send packet
		sent = clientSocket.sendto(pickle.dumps(sndpkt), serverAddress)
		print "Sent data with seq:", nextSeqnum, "and value:", sndpkt
#		increment variable nextSeqnum
		nextSeqnum = nextSeqnum + 1
#		check if EOF has reached
		if(iterator == 999):
			done = True
#		append packet to window
		window.append(sndpkt)
#		read more data
		iterator = iterator + 1

#RECEIPT OF AN ACK
	try:
		packet,serverAddress = clientSocket.recvfrom(4096)
		rcvpkt = []
		rcvpkt = pickle.loads(packet)
#		check value of checksum received (c) against checksum calculated (h) 
		c = rcvpkt[-1]
		del rcvpkt[-1]
		h = hashlib.md5()
		h.update(pickle.dumps(rcvpkt))
		if c == h.digest():
			print "Received ack for", rcvpkt[0]
#			slide window and reset timer
			print rcvpkt[0]> base and not(window is None) and window, rcvpkt[0], base, window
			while rcvpkt[0]> base and not(window is None):
				print "Ack done for", rcvpkt[0]
				lastackreceived = time.time()
				del window[0]
				base = base + 1
		else:
			print "error detected"
#TIMEOUT
	except:
		if(time.time()-lastackreceived>0.01):
			for i in window:
				sent = clientSocket.sendto(pickle.dumps(i), serverAddress)
	print done, window

print "connection closed"    
clientSocket.close()
