# PocketChat
PocketChat is a little chat program that I wrote in python with a UI made for the PocketChip.

Client patch notes for PocketChatIRC client V1.0:

NEW COMMANDS:
- Join a channel: /join #channel
- Leave a channel: /leave in the channel window you want to leave
- Send a pm: /msg user

Currently working:  
- Joining and leaving channels
- Private messages
- Online user list for all channels
- Online user list updates as users join, leave or change names

Client patch notes for PocketChatIRC client V0.5:
- Basic functionality working

Client patch notes for V0.5.1:

- Rewrote most of the client code to make it more object oriented.
- Removed many unnecessary lines of code.
- Fixed some error handling issues with usernames and empty text messages.
- Optimized most of the code.

Dependencies:

python3:

sudo apt-get install python3

python-tk:

sudo apt-get install python3-tk

To run the program: 

python3 PocketChatV0.5.1.py

Open port 5000 on PocketChip:

sudo iptables -A INPUT -p tcp --dport 5000 --jump ACCEPT 

sudo iptables-save
