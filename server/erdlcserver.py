#!/usr/bin/python
# -*- coding: utf-8 -*-
#El Rey de la Colina server

'''
 Enviar en la respuesta el tiempo restante para llegar a las 00:00 en una escala del 0 al 100 y usarlo en el frontend con la idea de Simón:
    Un caballero sobre su caballo portando un estandarte y cabalgando (gif?) hacia la izquierda sobre la barra de tiempo restante que estará sobre el <footer>
 El frontend sigue enviando solicitudes erroneas cuando se pulsa intro sobre elementos del formulario.
'''


import socket, json
import time
import urllib2
import pickle
import sys
import signal
from threading import Timer
from datetime import datetime

PORT = 15556
HOST = '127.0.0.1'

players = {}
playersSortedList = []
currentKing = None
alreadyReset = True
reigns = {}
reignsSortedList = []

class Player:
    def __init__(self,name,sex):
        self.name = name
        self.sex = sex
        self.lastEventDate = datetime.now()
        self.secondsThisWeek = 0
        
def newThroneClaim(name,sex):
    global players, currentKing
    print name, "(", sex, ")", "claims the throne."
    if (currentKing and (currentKing.name != name or currentKing.sex != sex)): #si ya hay un rey pero es distinto
        if(name in players): #si este ya existe
            currentPlayer = players[name]
            currentPlayer.sex = sex
            currentPlayer.lastEventDate = datetime.now()
            currentKing = currentPlayer
        else: #si este no existe
            print name,"has joined the game."
            players[name] = Player(name,sex)
            currentKing = players[name]
    elif (not currentKing): #si no hay rey
        print name,"is he first player to join the game."
        players[name] = Player(name,sex)
        currentKing = players[name]
        
def updateReignsSortedList():
    global reignsSortedList
    reignsSortedList = []
    for name in reigns:
        reignsSortedList.append((name, reigns[name]))            
    reignsSortedList = sorted(reignsSortedList, key=lambda x: x[1])
    reignsSortedList.reverse()
    
def backupReignsToFile():
    with open('erdlc.backup', 'wb') as f:
        pickle.dump(reigns, f, -1)
        print 'Backup file erdlc.backup saved.'
    
def restoreReignsFromFile():
    global reigns
    print 'Loading backup file...'
    try:
        with open('erdlc.backup', 'rb') as f:
            reigns = pickle.load(f)
            print 'Backup file restored (',len(reigns),'players added to the top',').'
    except IOError:
        print 'Backup file not found.'
    
def statusUpdate():
    global players, currentKing, playersSortedList, reignsSortedList, alreadyReset
    if(currentKing):
        # updating secondsThisWeek
        timeEarned = datetime.now() - currentKing.lastEventDate
        currentKing.lastEventDate = datetime.now()
        currentKing.secondsThisWeek += timeEarned.seconds + timeEarned.days*86400 + timeEarned.microseconds/1000000.
        # updating playersSortedList
        playersSortedList = []
        for player in players:
            playersSortedList.append((players[player].name,players[player].sex,int(round(players[player].secondsThisWeek))))            
        playersSortedList = sorted(playersSortedList, key=lambda x: x[2])
        playersSortedList.reverse()
    #if(datetime.today().weekday()==0 and not alreadyReset):
    if(datetime.now().hour==0 and not alreadyReset):
        # save winner of the week
        if(len(playersSortedList)>0):
            winner = playersSortedList[0][0]
            if(winner in reigns):
                reigns[winner] += 1
            else:
                reigns[winner] = 1
        # writing a backup file
        backupReignsToFile()
        # update reignsSortedList
        updateReignsSortedList()
        # reset weekly data
        players = {}
        playersSortedList = []
        currentKing = None
        alreadyReset = True
    #if(datetime.today().weekday()!=0):
    if(datetime.now().hour >= 1):
        alreadyReset = False
    t = Timer(0.1,statusUpdate,())
    t.setDaemon(True) #when the main thread receives the KeyboardInterrupt, if it doesn't catch it or catches it but decided to terminate anyway, the whole process will terminate.
    t.start()
    
def getTimeBarValue(): #returns current time in a 0-100 scale to be used in a progress bar
    currentTime = datetime.now().time()
    currentHour = currentTime.hour
    currentMinute = currentTime.minute
    ret = currentHour*100/24 + currentMinute*10/144
    return ret
    
def process(query): #processing query and returning json response
    if(query!="refresh"):
        name = urllib2.unquote(query.split('&')[0])
        sex = query.split('&')[1]
        newThroneClaim(name,sex)
    response = []        
    response.append(playersSortedList)
    if (currentKing):
        response.append((currentKing.name, currentKing.sex))
    else:
        response.append(('?', 'male'))
    response.append(reignsSortedList)
    response.append(getTimeBarValue())
    jsonResponse = json.dumps(response)
    return jsonResponse
    
def signal_handler(signal, frame):
    print 'Exiting...'
    sys.exit(0)

statusUpdate()

# for testing purpose only
reigns['Alexander the Great'] = 2
reigns['The BoSS'] = 7
# ---- ---- ---- ---- ----

restoreReignsFromFile()
updateReignsSortedList()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates tcp/ip socket
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    s.bind((HOST,PORT))
except socket.error, e:
    print e
    sys.exit(0)
s.listen(1)
print "Listening @",s.getsockname()
signal.signal(signal.SIGINT, signal_handler)
print "(press ctrl+c to exit)"
while True:
	s.settimeout(None)
	sc, sockname = s.accept()
	#print "Connection accepted from",sockname
	s.settimeout(0.5)
	try:
	    incomingmessage = sc.recv(999)
	except socket.timeout:
	    print '...waiting too long for a message, closing this connection.'
	    continue
	#print "Incoming message:",repr(incomingmessage)
	response = process(incomingmessage)
	
	try:
	    sc.sendall(response)
	    #print 'toma lacasitos'
	except socket.timeout:
	    print '...waiting too long to send our response, closing this connection.'
	    continue
	#print "Response has been sent"
