#!/usr/local/bin/python3
#  a manifest parser/tag watcher with SCTE base64 decoder
#
import re
import sys
import subprocess
import code
import time
import json
import os
from datetime import datetime
from time import gmtime, strftime
import pygments
from pygments import highlight, lexers, formatters
##
##
## == USER DEFINED SEARCH TERMS =============================================
##
TermsToFind = ["CUE","ENDLIST","SCTE35","DISCONTINUITY", "SEQUENCE","ERROR", "error","init.m4s","spot","Add-terms-here"]
#TermsToFind = ["CUE", "ENDLIST"]
##
## == DEFINE YOUR LOOP WAIT TIME Below 
TimeToSleep = 15
##
## ----  END of user defined terms ----------------------------------------
##
##
## = Color codes ============================================================
CBLUE ='\33[34m'
CRED  ='\33[31m'
CYELLOW ='\33[33m'
CWHITE  = '\33[37m'
CEND ='\33[0m'

##
print("\n\n\n",CYELLOW,"** HLS Child rendition manifest parser & tag checker **",CEND,"\n")
print("** This script prints any lines matching a list of user-defined keywords **","\n\n")
print("")
print("** This script reads the target manifest from a valid URL.")
print("----> Got a local file instead?")
print("----> You can start a local webserver in your dir by running 'python3 -m http.server' and browsing to http://localhost:8000/<<yourfile>>")

## ===========================================================================================

## --- Confirm threefive is installed or prompt for same & exit

try:
    import threefive
    from threefive import Stream
    from threefive import Cue
    print("")
except ModuleNotFoundError:
    print("!!  --> The needed python library 'threefive' is not installed, please install it via cmd 'pip install threefive' ")
    print("!!")
    exit()

## ===========================================================================================
## Get and check target URL...

INSTRING="nope"
try:
	INSTRING = sys.argv[1]

except:	
	INSTRING = input ("Enter a URL for a valid HLS child manifest : ")

if not (( INSTRING[0]=="'") or (INSTRING[0]=='h') or(INSTRING[0]=='"') ):
	print("possibly invalid input URL.. .")
	#exit()

##
TURL = INSTRING
TargetURL = TURL
urlwords = TURL.split("m")
if ".m3u8" in INSTRING:
	print(".")
else:
	print("\n","!! --> Invalid URL?  exiting.")
	exit()
	
##
## ===========================================================================================
def decodemarker( rawstring ):
	global rstring
	rstring = rawstring
	print(CBLUE,"--> attempting to decode marker...",CEND)
	#code.interact()
	if not ( rstring[0]=="/"):
		print("Unparseable base64..skipping")
		return()
	
	try:
		import threefive
		cue = threefive.Cue(rstring)


	except:
		print("cue operation failed")
		
	if not (cue.decode()): 
		print("Could not decode the b64.")
		return()
	
	## remove these bits
	cue.bites='0'
	WIP=str(cue)
	WIP=WIP.replace("'",'"')
	WIP=WIP.replace('None','"None"')
	WIP=WIP.replace('True','"True"')
	WIP=WIP.replace('False','"False"')
	
	##
	import pygments
	from pygments import highlight, lexers, formatters
	interim_json = json.loads(WIP)
	formerly_json = json.dumps(interim_json, indent=4)
	colorful_json = highlight(formerly_json, lexers.JsonLexer(), formatters.Terminal256Formatter(style='emacs'))
	print("\n\n")
	print(colorful_json)
	print("\n\n")
    
	return()
  
## ===========================================================================================
##  retrieve the taget file  & Parse
##
TTS = TimeToSleep
while True : 
	CMD = "curl -s '"+TargetURL+"'"
	data = os.popen(CMD).read()
	input_file = data.splitlines()
	tnow = datetime.now()
	print("-->Current Timestamp: ",tnow,"\n")
	printnext = False
	
## =  interate through lines ==============================================================
	linecount = 0
	totalsegmenttime = 0.0
	
	for line in input_file:
		linecount = linecount + 1
		if ( printnext ) :
			#print("\n")
			print(CYELLOW,end='')
			print(" Followed by:",line,CEND,"\n")

			
		# compare each word in the line against TermsToFind
				
		text = re.split('[:,-]',line,flags=re.IGNORECASE)
		Done = False
		
		if ("EXTINF" in text[0]):
			totalsegmenttime = totalsegmenttime + float(text[1])
			
			
		
		for Z in range (0,(len(TermsToFind))):
			if Done :
				break
				
			#print("comparing: ",TermsToFind[Z], " and ", text)
			
			
			if TermsToFind[Z] in text:
				print(CWHITE)
				print("Line ", end='')
				print("{:04d}".format(linecount), ":",CEND, end='')
				print(CBLUE," Found:      ",line,CEND, end='')
				## special cases: 
				
				if ("ENDLIST" in text):
					print("\n\n",CWHITE)
					print("Found ENDLIST tag in source; exiting now.")
					totalsegmenttime = round(totalsegmenttime, 3) 
					print("\n")
					print("Total segment duration of all segments was:",totalsegmenttime,"s")
					print(CEND)
					exit()
				
				##
				if (("CUE-OUT" in line) and not ("CUE-OUT:" in line)):
					print(CRED,end='' )
					print("!! Found CUE-OUT without Duration.",CEND)
					print("                          ",end='')
				
				##
				if ("SCTE35" in TermsToFind[Z]):
					print("\n")
					## find the base64
					try: 
						
						RAWMARKER = str(text[3])
						RAWMARKER=RAWMARKER.replace('CUE=','')
						base64=RAWMARKER.replace('"','')
						print("\n")
						try:
							DC=decodemarker(base64)
							#print(DC)
						
						except:
							print(".") ## function called failed?
					
					except:
						print("Couldn't call base64_decode.py")
				
				
				printnext = True
				Done = True
			else:
				printnext = False
	
	print("\n")
	totalsegmenttime = round(totalsegmenttime, 3)
	print("Total segment duration of all segments was:",totalsegmenttime,"s")
	print("\n")
	print("...waiting",TTS,"sec.","\n\n\n")
	time.sleep(TTS)
      
      
print("\n","--done--")      
    