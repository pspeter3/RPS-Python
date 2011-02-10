#!/usr/bin/python

#rpskumo
screenname=""
password=""
host=("login.oscar.aol.com", 5190)
profile="Rock Paper Scissors<br>Phips Peter<br>Version 0.4"

#imports
from twisted.words.protocols import oscar
from twisted.internet import protocol, reactor
from rpsengine import engine
from re import sub
from time import localtime, strftime

rps=engine()
data={}
tk={"r":0,"p":1,"s":2}
kt=["rock","paper","scissors"]
disp=["You won","We tied","You lost"]

def PARSE(usr,cmd):
	temp=cmd
	if len(cmd)>0: cmd=cmd[0]
	else: cmd="h"
	cmd=cmd.lower()
	o=0
	if cmd=="r" or cmd=="p" or cmd=="s":
		k=rps.think(usr)
		l=tk[cmd]
		m=rps.update(k,l,usr)
		return "I chose %s. %s" %(kt[k],disp[m])
		o=1	if cmd=="h":
		return "<br>*Type 'h' for help<br>*Type 'g' for global stats<br>*Type 'x' for stats<br>*Type 'r' for rock<br>*Type 'p' for paper<br>*Type 's' for scissors<br>"
		o=1
	if cmd=="x":
		return "<br>Wins: %s <br>Draws: %s <br>Losses: %s <br>Total: %s <br>Ratio: %s"%rps.xstat(usr)
		o=1
	if cmd=="g":
		return "<br>Wins: %s <br>Draws: %s <br>Losses: %s <br>Total: %s <br>Ratio: %s" %rps.gstat()
	if cmd=="m":
		r=temp.split(" ")
		if r[1]=="hurricane" and len(r)>2: return "<br>Wins: %s <br>Draws: %s <br>Losses: %s <br>Total: %s <br>Ratio: %s"%rps.xstat(r[2])
	if cmd=="n":
		r=temp.split(" ")
		if r[1]=="hurricane": return str(rps.data.keys())
	if o==0:
		return "Invalid command. Type 'h' for help"

def normalize(data):
	data=sub("<[^>]*>","",data)	
	return data.lstrip()
#bot class
class bot(oscar.BOSConnection):
	capabilities = [oscar.CAP_CHAT]
	def initDone(self):
		self.requestSelfInfo().addCallback(self.gotSelfInfo)
		self.requestSSI().addCallback(self.gotBuddyList)
	def gotSelfInfo(self,user):
		self.name=user.name
	def gotBuddyList(self,l):
		self.activateSSI()
		self.setProfile(profile)
		self.setIdleTime(0)
		self.clientReady()
	def receiveMessage(self, user, multiparts, flags):
		cmd=multiparts[0][0]
		cmd=normalize(cmd)
		output=PARSE(user.name,cmd)
		self.sendMessage(user.name,output)
		time=strftime("(%H:%M:%S)",localtime())
		print "%s%s: %s" %(time,user.name,cmd)

class root(oscar.OscarAuthenticator):
	BOSClass=bot

protocol.ClientCreator(reactor,root,screenname,password).connectTCP(*host)
print "CONNECTED..."
reactor.run()
