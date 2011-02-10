"""Rock Paper Scissors Engine
Phips Peter
Version 0.5"""

#imports
from random import randint
from os.path import exists
from os import mkdir

#profile struct used for data storage
class profile_struct:
	def __init__(self):
		#queues for history, comp being the computer, humn being the human player
		self.comp=[]
		self.humn=[]
		#records, w is wins, l is losses, d is draws, t is total number of games, r is w/(w+l) the goal is for it to be less than 50%
		self.w=0
		self.d=0
		self.l=0
		self.t=0
		self.r=0.0
	def disp(self):
		#returns data
		return self.w,self.d,self.l,self.t,self.r	
	def append(self,comp,humn,qmax):
		#appends the queues
		if len(self.comp)>qmax:
			self.comp.pop(0)
			self.humn.pop(0)
			self.comp.append(comp)
			self.humn.append(humn)
		else:
			self.comp.append(comp)
			self.humn.append(humn)
	def record(self,value):
		#changes win loss record
		if value==0:self.w+=1
		if value==1:self.d+=1
		if value==2:self.l+=1
		self.t+=1
		if (self.w+self.l)>0: self.r=float(self.w)/(self.w+self.l)

#actual AI engine
class engine:
	def __init__(self,template_length=5,queue_max=50,logging=False):
		#the max length of the search criteria 		
		self.leaf=template_length
		#the max length of history to be stored
		self.root=queue_max
		#a boolean which tells the engine whether or not to log data
		self.log=logging
		#a dictionary of profiles, useful for playing against multiple opponents, as is the case of a bot
		self.data={}
		#a floating point that exists in rock, paper, scissors space and is used for a moving average in the anyl function
		self.mind=[0,0,0]
		#global records (see profile struct for meaning of variable names)
		self.w,self.d,self.l,self.t,self.r=0,0,0,0,0.0
		#checks to see if the data has been stored and then assign it
		if exists("global.txt") and self.log:
			gfile=open("global.txt")
			temp=gfile.read().split(" ")
			self.w,self.d,self.l,self.t,self.r=int(temp[0]),int(temp[1]),int(temp[2]),int(temp[3]),float(temp[4])
		#make a directory for data
		if not exists("profiles") and self.log: mkdir("profiles")	
	
	def write(self,profile):
		#if logging is on, log data		
		if self.log:	
			#filename to write data to
			fname="profiles/%s.csv" %profile
			#fileoutput		
			output = "%s,%s,%s,%s,%s\n" %self.data[profile].disp()
			#open and write to file
			csv=open(fname,"a")
			csv.write(output)
			csv.close
			log=open("global.txt","w")
			log.write("%s %s %s %s %s" %self.gstat())
			log.close()

	def find(self,base,srch):
		#searches list for sublist		
		n=len(srch)
		k=len(base)-n
		hist=[]
		count=0
		i=0
		run=True
		while i<k:
			if base[i:i+n]==srch: 
				hist.append(i)
				count+=1
			i+=1
		return count,hist
	
	def check(self,usr,opp):
		#checks for win or loss
		r=[1,2,0]
		p=[0,1,2]
		s=[2,0,1]
		ck=[r,p,s]
		return ck[usr][opp]
	
	def record(self,value):
		#changes win loss record
		if value==0:self.w+=1
		if value==1:self.d+=1
		if value==2:self.l+=1
		self.t+=1
		if (self.w+self.l)>0: self.r=float(self.w)/(self.w+self.l)

	def update(self,comp,humn,profile="sudo"):
		#update values
		self.data[profile].append(comp,humn,self.root)
		#calculate win loss or draw
		c=self.check(comp,humn)
		h=self.check(humn,comp)
		#update records
		self.record(c)
		self.data[profile].record(h)
		#write data
		self.write(profile)
		#return player
		return h

	def xstat(self,profile="sudo"):
		if not self.data.has_key(profile):
			self.data[profile]=profile_struct()
			if self.log:
				fname="profiles/%s.csv" %profile
				csv=open(fname,"a")
				csv.write("wins,draws,losses,total,ratio\n")
				csv.close()
		return self.data[profile].disp()

	def gstat(self):
		return self.w,self.d,self.l,self.t,self.r

	def anyl(self,flag,hist,profile):
		#figure out what queue to look at
		if flag==0: temp=self.data[profile].comp
		else: temp=self.data[profile].humn
		#split the queue into pattern(srch) and history(temp)
		srch=temp[len(temp)-hist:len(temp)]
		temp=temp[0:len(temp)-hist]
		#count how many patterns and get indexs of the pattern		
		count,indexs=self.find(temp,srch)
		#calculate weight for exponential smoothing
		#weight=(number of pattern)/((length of history)/(length of pattern))
		var=len(temp)/float(len(srch))
		weight=count/var
		#loop through indexs
		for i in indexs:
			#temp floating point in rps space for exponential smoothing
			t=[0,0,0]
			#index to check is equal to index i + history
			indx=i+hist
			#smoothing index
			smooth=self.data[profile].humn[indx]
			#set temp point index
			t[smooth]=1
			#loop through and combine the points
			for k in range(3):
				self.mind[k]=(self.mind[k]*(1-weight))+(t[k]*weight)

	def think(self,profile="sudo"):
		#if profile doesn't exist, make it
		if not self.data.has_key(profile):
			self.data[profile]=profile_struct()
			if self.log:
				fname="profiles/%s.csv" %profile
				csv=open(fname,"a")
				csv.write("wins,draws,losses,total,ratio\n")
				csv.close()
		#reset mind point
		self.mind=[0,0,0]
		#check if there is enough data
		if self.leaf>=len(self.data[profile].humn): return randint(0,2)
		else:
			#loop
			for i in range(1,self.leaf):
				for k in range(2):
					self.anyl(k,i,profile)
			#temp variables
			temp=0
			j=-1
			#dictionary of responses
			do={-1:randint(0,2),0:1,1:2,2:0}
			#check for which is the most likely move to occur
			for i in range(3):
				r=self.mind[i]
				if r>temp:
					temp=r
					j=i
			#respond to the move
			return do[j]
