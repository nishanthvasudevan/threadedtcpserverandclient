#!/usr/bin/python

import os
import sys
import SocketServer
import difflib
from operator import itemgetter


def initdb(vcodedbfile, vcodedbrev):
	f = open(vcodedbfile,'r')
	for line in f.read().split('\n'):
		if line:
			parts = line.split('\t')
			vcodeTitle = parts[1].split('|')[1].replace(' ','').upper()
			p = parts[1].split('|')
			path = p[11].split('/')
			pOfPath = path[4]
			vcodeContent = parts[0]+'|'+pOfPath
			val = "%s" % (vcodeTitle)
			tmp = set()
			if vcodedbrev.has_key(val):
				tmp = vcodedbrev[val]
			if tmp:
				tmp |= set([vcodeContent])
			else:
				tmp = set([vcodeContent])
			vcodedbrev[val] = tmp
	f.close()

vcodedbrev={}
vcodefile = sys.argv[1]
port = sys.argv[2]
initdb(vcodefile, vcodedbrev)

print "Starting server port="+port

class EchoRequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		query = self.request.recv(1024)
		orig_query = query
		if query.find(':VCODE') != -1:
			vCode = query
			vCode = vCode.replace(' ','')
			vCode = vCode.split(':')[0]
			for key in vcodedbrev.keys():
				vcodes = vcodedbrev[key]
				for vcode in vcodes:
					code = vcode.split('|')[0]
					if vCode == code:
						contents = vcode+"\n"
						self.request.send(contents)
		else:
			query = query.replace(' ','').upper()
			guesses = difflib.get_close_matches(query,vcodedbrev.keys(),50,0.85)

			res = {}	
			for key in vcodedbrev.keys():
				if query in key:
					score = 0.999
					vcodes = vcodedbrev[key]
					for vcode in vcodes:
						vcode_title = vcode+"|"+key+"|SUBSTRING"
						res[vcode_title] = score
				for guess in guesses:
					if key == guess:
						difflibScore = round((difflib.SequenceMatcher(lambda x: x == " ", query, guess)).ratio(), 3)
						score = difflibScore
						vcodes = vcodedbrev[key]
						for vcode in vcodes:
							vcode_title = vcode+"|"+key+"|FUZZY"
							res[vcode_title] = score
			
			items = res.items()
			items.sort(key = itemgetter(1), reverse=True)
			vcodes = ""
			logtext = ""
			for item in items:
				vcodes += "%s|%s\n" % (item[0],item[1])
				logtext += "%s|%s," % (item[0],item[1])
			log = "INFO: QUERY=%s,RESULT=%s\n" % (orig_query,logtext)
			sys.stdout.write(log)
			sys.stdout.flush()
			
			contents = vcodes
			self.request.send(contents)

server = SocketServer.ThreadingTCPServer(('',int(port)), EchoRequestHandler)
server.serve_forever()
