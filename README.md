# PocketChat
PocketChat is a little chat program that I wrote in python with a UI made for the PocketChip.

COMMANDS:
- Join a channel: /join #channel
- Leave a channel: /leave in the window of the channel you want to leave
- Send a pm: /msg user

Client patch notes for PocketChatIRC client V1.5:
- Fixed an issue with the receiving loop that was causing high cpu usage
- Fixed segmentation fault

Client patch notes for PocketChatIRC client V1.4:
- Fixed bug where some of the incoming text was being added to the online user list
- Added timestamps

Client patch notes for PocketChatIRC client V1.2:
- Fixed bug where all users where not being adding to the online user list properly
- Added filtering for NOTICE messages from the server
- Changed what is being shown on other incoming messages being posted in the main window

Client patch notes for PocketChatIRC client V1.1:
- Fixed bug that caused an indexing issue with incoming messages

Client patch notes for PocketChatIRC client V1.0:
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
