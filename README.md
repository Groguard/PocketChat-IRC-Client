# PocketChat
PocketChat is a light weight IRC client that I wrote in python with a UI made for the PocketChip, but
it can also be used on windows and linux.

<a href="http://imgur.com/RmCt5iu"><img src="http://i.imgur.com/RmCt5iu.png" title="source: imgur.com" /></a>

# COMMANDS:
- Join a channel: /join #channel
- Leave a channel: /leave in the window of the channel you want to leave
- Send a pm: /msg user message
- Change you nick: /nick newname
- Close the client: /quit
- Auto join channels by adding them to the box seperated by commas no spaces e.g.(#chipsters,#nextthingco,#linux)

# Client patch notes for PocketChatIRC client V2.0:
- Added nickname, identity, and realname persistance
- Added autojoin channels feature

# Client patch notes for PocketChatIRC client V1.9.2:
- Fixed login screen UI sizing on PocketChip

# Client patch notes for PocketChatIRC client V1.9.1:
- Cleaned up more code in the tabbing system increasing speed
- Cleaning up naming space for easier code readability
- Removed several for loops through out by changing a few things with the dictionaries, increasing speed

# Client patch notes for PocketChatIRC client V1.9:
- Removed over 30 lines of repetitive code while keeping functionality
- Added option to change IRC server
- Fixed bug with sending a pm where the case wasn't the same as on the server, causing a new tab to open

# Client patch notes for PocketChatIRC client V1.8:
- Fixed bug where only a part of the users message would be sent

# Client patch notes for PocketChatIRC client V1.7:
- Added quit function to close the program when a user types /quit in any tab.

# Client patch notes for PocketChatIRC client V1.6:
- Better formating for incoming text from server
- Added message filtering for incoming QUIT commands
- Added message filtering for incoming ACTION commands e.g.(*user did something)
- Added /nick command to change nick while connected
- Added SSL connection option
- Added password option for registered usernames
- Added online user count to online list

# Client patch notes for PocketChatIRC client V1.5:
- Fixed an issue with the receiving loop that was causing high cpu usage
- Fixed segmentation fault

# Client patch notes for PocketChatIRC client V1.4:
- Fixed bug where some of the incoming text was being added to the online user list
- Added timestamps

# Client patch notes for PocketChatIRC client V1.2:
- Fixed bug where all users where not being adding to the online user list properly
- Added filtering for NOTICE messages from the server
- Changed what is being shown on other incoming messages being posted in the main window

# Client patch notes for PocketChatIRC client V1.1:
- Fixed bug that caused an indexing issue with incoming messages

# Client patch notes for PocketChatIRC client V1.0:
- Joining and leaving channels
- Private messages
- Online user list for all channels
- Online user list updates as users join, leave or change names

# Client patch notes for PocketChatIRC client V0.5:
- Basic functionality working

# Dependencies:

- sudo apt-get install python3
- sudo apt-get install python3-tk
- run the program: 
  python3 PocketChatIRCV.py
