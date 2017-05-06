# -*- coding: utf-8 -*-

import sys


_ipcmsg_awaitinput	= '!AWAIT'
_ipcmsg_sendoutput	= '!MESSAGE:'
_ipcmsg_terminate	= '!TERMINATE'


def _printToStd(msg):
	print(msg)
	sys.stdout.flush()

def sendAwait():
	_printToStd(_ipcmsg_awaitinput)

def sendTerminate():
	_printToStd(_ipcmsg_terminate)

def sendMessage(msg):
	_printToStd(_ipcmsg_sendoutput + str(msg))


def receive():
	line	= sys.stdin.readline()
	#_printToStd("receive() : {}".format(line))
	return line.rstrip() if line else line

