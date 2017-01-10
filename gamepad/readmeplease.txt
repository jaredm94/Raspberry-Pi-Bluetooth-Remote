  
  #######################################################################################################################################################################################################################################################################################################################################################
  This is the actual gamepad code.My documentation of setting up the bluetooth was questionable at best
so ill try to give the gist of what 
I hope to accomplish intially and add things of interest as I go. I plan on modifying the code
from the example that inspired this, these modifications will primarily come in the form of me 
replacing the keyboard class with a gamepad class.This abstraction will be responsable for sending
messages in the joystick/gamepad forat to my amazon fire tv via gesture controlled commands(Skywriter).
I will also makes some changes to the advertising of the pi so it appears as a joystick instead of a 
keyboard. The stack structure for a joystick bluetooth message is also different from its 
keyboard counterpart.
