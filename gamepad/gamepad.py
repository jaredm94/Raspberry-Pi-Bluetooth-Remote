#!/usr/bin/python

import os
import sys
import dbus
import dbus.service
import dbus.mainloop.glib
import time
import evdev # used to get input from the keyboard
from evdev import *
#import keymap # used to map evdev input to hid keodes

class Gamepad():

	def __init__(self):


		D_Pad_Left = 0x93

		D_Pad_Right = 0x92

		D_Pad_Down = 0x91

		D_Pad_Up = 0x90

		self.state = [
			0xFD, #Raw Report mode.
			0x06, #Size of
			0x00, #Buttons being pressed
			0x00, #X1
			0x00, #send_pad Y1
			0x00, #X2
			0x00, #Y2
		]


		print "setting up DBus Client"

		self.bus = dbus.SystemBus()
		self.btkservice = self.bus.get_object('org.yaptb.btkbservice', '/org/yaptb/btkbservice')
		self.iface = dbus.Interface(self.btkservice, 'org.yaptb.btkbservice')


	#forward keyboard events to the dbus service
   	def send_input(self):

		bin_str=""
		element=self.state[2]
		for bit in element:
			bin_str += str(bit)



		self.iface.send_pad(self.state)



if __name__ == "__main__":

	print "Setting up keyboard"

	#kb = Keyboard()

	print "starting event loop"
	#kb.event_loop()

	game = Gamepad()

	for i in range(0,100,1):
		time.sleep(4)
		self.state[2] = 0x91
		game.send_input()
		self.state[2] = 0x00
		game.send_input()


