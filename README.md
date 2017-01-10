# Raspberry-Pi-Bluetooth-Remote
A bluetooth remote for my amazon fire stick


1. Raspberry Pi 3 B+ so we have built in blue tooth.


Roving Networks Bluetooth HID Profile:

Structure of bluetooth message for joystick found: pg 7 
Key mappings: pg 8

To setup the pi and configuring the bluetooth slave broadcast message
https://www.gadgetdaily.xyz/create-a-cool-sliding-and-scrollable-mobile-menu/


HID values hopefully:(http://www.freebsddiary.org/APC/usb_hid_usages.php)

help with connecting
http://python-evdev.readthedocs.io/en/latest/tutorial.html



http://www.bluez.org/bluez-5-api-introduction-and-porting-guide/
http://yetanotherpointlesstechblog.blogspot.com/2016/04/emulating-bluetooth-keyboard-with.html

 bluetoothctl


Here the line for the Bluetooth Daemon Configuration (tested on Ubuntu)
In the file /etc/systemd/system/dbus-org.bluez.service
Replace the line ExecStart by:
ExecStart=/usr/lib/bluetooth/bluetoothd -P input

To advertise as something else: http://www.question-defense.com/tools/class-of-device-bluetooth-cod-list-in-binary-and-hex
                               http://askubuntu.com/questions/439088/how-to-change-bluetooth-device-class
                               http://netlab.cs.ucla.edu/wiki/files/class_of_device.pdf
http://bluetooth-pentest.narod.ru/software/bluetooth_class_of_device-service_generator.html
