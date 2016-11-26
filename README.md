# PocketChat
PocketChat is a little chat program that I wrote in python with a UI made for the PocketChip.
It can also be used on windows and linux.

COMMANDS:
- Join a channel: /join #channel
- Leave a channel: /leave in the window of the channel you want to leave
- Send a pm: /msg user
- Change you nick: /nick newname
- Close the client: /quit

Client patch notes for PocketChatIRC client V1.9:
- Removed over 30 lines of repetitive code
- Added option to change IRC server
- Fixed bug with sending a pm where the case wasn't the same as on the server, causing a new tab to open

Client patch notes for PocketChatIRC client V1.8:
- Fixed bug where only a part of the users message would be sent

Client patch notes for PocketChatIRC client V1.7:
- Added quit function to close the program when a user types /quit in any tab.

Client patch notes for PocketChatIRC client V1.6:
- Better formating for incoming text from server
- Added message filtering for incoming QUIT commands
- Added message filtering for incoming ACTION commands e.g.(*user did something)
- Added /nick command to change nick while connected
- Added SSL connection option
- Added password option for registered usernames
- Added online user count to online list

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
