#**********************************************#
## This was taken from https://github.com/Mqrius/BluePloverPi/blob/master/PiTooth.py
## and then modified to be used for the amazon firetv. Its identified as a "joystick"
## rather then a "keyboard" like it was in the original file.
#**********************************************#

#!/usr/bin/python2.7
#Code fixed from http://www.linuxuser.co.uk/tutorials/emulate-a-bluetooth-keyboard-with-the-raspberry-pi

import os
import sys
import bluetooth
from bluetooth import *
import dbus
import time
import evdev
from evdev import *
import keymap

class Bluetooth:
  P_CTRL = 17
  P_INTR = 19

  HOST = 0
  PORT = 1

  def __init__(self):
    os.system("hciconfig hci0 class 0x002540")
    os.system("hciconfig hci0 name Raspberry\ Pi")
    os.system("hciconfig hci0 piscan")
    self.scontrol = BluetoothSocket(L2CAP)
    self.sinterrupt = BluetoothSocket(L2CAP)
    self.scontrol.bind(("", Bluetooth.P_CTRL))
    self.sinterrupt.bind(("", Bluetooth.P_INTR))
    self.bus = dbus.SystemBus()

    self.manager = dbus.Interface(self.bus.get_object("org.bluez", "/"), "org.bluez.Manager")
    adapter_path = self.manager.DefaultAdapter()
    self.service = dbus.Interface(self.bus.get_object("org.bluez", adapter_path), "org.bluez.Service")

    with open(sys.path[0] + "/sdp_record.xml", "r") as fh:
      self.service_record = fh.read()

  def listen(self):
    self.service_handle = self.service.AddRecord(self.service_record)
    print "Service record added"
    self.scontrol.listen(1) # Limit of 1 connection
    self.sinterrupt.listen(1)
    print "Waiting for a connection"
    self.ccontrol, self.cinfo = self.scontrol.accept()
    print "Got a connection on the control channel from " + self.cinfo[Bluetooth.HOST]
    self.cinterrupt, self.cinfo = self.sinterrupt.accept()
    print "Got a connection on the interrupt channel fro " + self.cinfo[Bluetooth.HOST]

  def send_input(self, ir):
    #  Convert the hex array to a string
    hex_str = ""
    for element in ir:
      if type(element) is list:
        # This is our bit array - convrt it to a single byte represented
        # as a char
        bin_str = ""
        for bit in element:
          bin_str += str(bit)
        hex_str += chr(int(bin_str, 2))
      else:
        # This is a hex value - we can convert it straight to a char
        hex_str += chr(element)
    # Send an input report
    self.cinterrupt.send(hex_str)

class Keyboard():
  def __init__(self):
    # The structure for an bt keyboard input report (size is 10 bytes)
    self.state = [
         0xA1, # This is an input report
         0x01, # Usage report = Keyboard
         # Bit array for Modifier keys
         [0,   # Right GUI - (usually the Windows key)
          0,   # Right ALT
          0,   # Right Shift
          0,   # Right Control
          0,   # Left GUI - (again, usually the Windows key)
          0,   # Left ALT
          0,   # Left Shift
          0],   # Left Control
         0x00,  # Vendor reserved
         0x00,  # Rest is space for 6 keys
         0x00,
         0x00,
         0x00,
         0x00,
         0x00 ]

    # Keep trying to get a keyboard
    have_dev = False
    while have_dev == False:
      try:
        # Try and get a keyboard - should always be event0 as we.re only
        # plugging one thing in
        self.dev = InputDevice("/dev/input/event0")
        have_dev = True
      except OSError:
        print "Keyboard not found, waiting 3 seconds and retrying"
        time.sleep(3)
      print "Found a keyboard"

  def change_state(self, event):
    evdev_code = ecodes.KEY[event.code]
    modkey_element = keymap.modkey(evdev_code)
    if modkey_element > 0:
      # Need to set one of the modifier bits
      if self.state[2][modkey_element] == 0:
        self.state[2][modkey_element] = 1
      else:
        self.state[2][modkey_element] = 0
    else:
      # Get the hex keycode of the key
      hex_key = keymap.convert(evdev_code)
      # Loop through elements 4 to 9 of the input report structure
      for i in range (4, 10):
        if self.state[i] == hex_key and event.value == 0:
          # Code is 0 so we need to depress it
          self.state[i] = 0x00
          break
        elif self.state[i] == 0x00 and event.value == 1:
          # If the current space is empty and the key is being pressed
          self.state[i] = hex_key
          break

  def event_loop(self, bt):
    for event in self.dev.read_loop():
      # Only bother if we hit a key and it's an up or down event
      if event.type == ecodes.EV_KEY and event.value < 2:
        self.change_state(event)
        bt.send_input(self.state)

if __name__ == "__main__":
  if not os.geteuid() == 0:
    sys.exit("Only root can run this script")
  bt = Bluetooth()
  bt.listen()
  kb = Keyboard()
  kb.event_loop(bt)

  keytable = {
    "KEY_RESERVED" : 0,
    "KEY_ESC" : 41,
    "KEY_1" : 30,
    "KEY_2" : 31,
    "KEY_3" : 32,
    "KEY_4" : 33,
    "KEY_5" : 34,
    "KEY_6" : 35,
    "KEY_7" : 36,
    "KEY_8" : 37,
    "KEY_9" : 38,
    "KEY_0" : 39,
    "KEY_MINUS" : 45,
    "KEY_EQUAL" : 46,
    "KEY_BACKSPACE" : 42,
    "KEY_TAB" : 43,
    "KEY_Q" : 20,
    "KEY_W" : 26,
    "KEY_E" : 8,
    "KEY_R" : 21,
    "KEY_T" : 23,
    "KEY_Y" : 28,
    "KEY_U" : 24,
    "KEY_I" : 12,
    "KEY_O" : 18,
    "KEY_P" : 19,
    "KEY_LEFTBRACE" : 47,
    "KEY_RIGHTBRACE" : 48,
    "KEY_ENTER" : 40,
    "KEY_LEFTCTRL" : 224,
    "KEY_A" : 4,
    "KEY_S" : 22,
    "KEY_D" : 7,
    "KEY_F" : 9,
    "KEY_G" : 10,
    "KEY_H" : 11,
    "KEY_J" : 13,
    "KEY_K" : 14,
    "KEY_L" : 15,
    "KEY_SEMICOLON" : 51,
    "KEY_APOSTROPHE" : 52,
    "KEY_GRAVE" : 53,
    "KEY_LEFTSHIFT" : 225,
    "KEY_BACKSLASH" : 50,
    "KEY_Z" : 29,
    "KEY_X" : 27,
    "KEY_C" : 6,
    "KEY_V" : 25,
    "KEY_B" : 5,
    "KEY_N" : 17,
    "KEY_M" : 16,
    "KEY_COMMA" : 54,
    "KEY_DOT" : 55,
    "KEY_SLASH" : 56,
    "KEY_RIGHTSHIFT" : 229,
    "KEY_KPASTERISK" : 85,
    "KEY_LEFTALT" : 226,
    "KEY_SPACE" : 44,
    "KEY_CAPSLOCK" : 57,
    "KEY_F1" : 58,
    "KEY_F2" : 59,
    "KEY_F3" : 60,
    "KEY_F4" : 61,
    "KEY_F5" : 62,
    "KEY_F6" : 63,
    "KEY_F7" : 64,
    "KEY_F8" : 65,
    "KEY_F9" : 66,
    "KEY_F10" : 67,
    "KEY_NUMLOCK" : 83,
    "KEY_SCROLLLOCK" : 71,
    "KEY_KP7" : 95,
    "KEY_KP8" : 96,
    "KEY_KP9" : 97,
    "KEY_KPMINUS" : 86,
    "KEY_KP4" : 92,
    "KEY_KP5" : 93,
    "KEY_KP6" : 94,
    "KEY_KPPLUS" : 87,
    "KEY_KP1" : 89,
    "KEY_KP2" : 90,
    "KEY_KP3" : 91,
    "KEY_KP0" : 98,
    "KEY_KPDOT" : 99,
    "KEY_ZENKAKUHANKAKU" : 148,
    "KEY_102ND" : 100,
    "KEY_F11" : 68,
    "KEY_F12" : 69,
    "KEY_RO" : 135,
    "KEY_KATAKANA" : 146,
    "KEY_HIRAGANA" : 147,
    "KEY_HENKAN" : 138,
    "KEY_KATAKANAHIRAGANA" : 136,
    "KEY_MUHENKAN" : 139,
    "KEY_KPJPCOMMA" : 140,
    "KEY_KPENTER" : 88,
    "KEY_RIGHTCTRL" : 228,
    "KEY_KPSLASH" : 84,
    "KEY_SYSRQ" : 70,
    "KEY_RIGHTALT" : 230,
    "KEY_HOME" : 74,
    "KEY_UP" : 82,
    "KEY_PAGEUP" : 75,
    "KEY_LEFT" : 80,
    "KEY_RIGHT" : 79,
    "KEY_END" : 77,
    "KEY_DOWN" : 81,
    "KEY_PAGEDOWN" : 78,
    "KEY_INSERT" : 73,
    "KEY_DELETE" : 76,
    "KEY_MUTE" : 239,
    "KEY_VOLUMEDOWN" : 238,
    "KEY_VOLUMEUP" : 237,
    "KEY_POWER" : 102,
    "KEY_KPEQUAL" : 103,
    "KEY_PAUSE" : 72,
    "KEY_KPCOMMA" : 133,
    "KEY_HANGEUL" : 144,
    "KEY_HANJA" : 145,
    "KEY_YEN" : 137,
    "KEY_LEFTMETA" : 227,
    "KEY_RIGHTMETA" : 231,
    "KEY_COMPOSE" : 101,
    "KEY_STOP" : 243,
    "KEY_AGAIN" : 121,
    "KEY_PROPS" : 118,
    "KEY_UNDO" : 122,
    "KEY_FRONT" : 119,
    "KEY_COPY" : 124,
    "KEY_OPEN" : 116,
    "KEY_PASTE" : 125,
    "KEY_FIND" : 244,
    "KEY_CUT" : 123,
    "KEY_HELP" : 117,
    "KEY_CALC" : 251,
    "KEY_SLEEP" : 248,
    "KEY_WWW" : 240,
    "KEY_COFFEE" : 249,
    "KEY_BACK" : 241,
    "KEY_FORWARD" : 242,
    "KEY_EJECTCD" : 236,
    "KEY_NEXTSONG" : 235,
    "KEY_PLAYPAUSE" : 232,
    "KEY_PREVIOUSSONG" : 234,
    "KEY_STOPCD" : 233,
    "KEY_REFRESH" : 250,
    "KEY_EDIT" : 247,
    "KEY_SCROLLUP" : 245,
    "KEY_SCROLLDOWN" : 246,
    "KEY_F13" : 104,
    "KEY_F14" : 105,
    "KEY_F15" : 106,
    "KEY_F16" : 107,
    "KEY_F17" : 108,
    "KEY_F18" : 109,
    "KEY_F19" : 110,
    "KEY_F20" : 111,
    "KEY_F21" : 112,
    "KEY_F22" : 113,
    "KEY_F23" : 114,
    "KEY_F24" : 115
}

# Map modifier keys to array element in the bit array
modkeys = {
   "KEY_RIGHTMETA" : 0,
   "KEY_RIGHTALT" : 1,
   "KEY_RIGHTSHIFT" : 2,
   "KEY_RIGHTCTRL" : 3,
   "KEY_LEFTMETA" : 4,
   "KEY_LEFTALT": 5,
   "KEY_LEFTSHIFT": 6,
   "KEY_LEFTCTRL": 7
}

def convert(evdev_keycode):
    return keytable[evdev_keycode]

def modkey(evdev_keycode):
    if evdev_keycode in modkeys:
        return modkeys[evdev_keycode]
    else:
        return -1 # Return an invalid array element
