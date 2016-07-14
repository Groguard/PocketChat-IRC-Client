# PocketChat
Chat program made for PocketChip


Dependencies:


python3:
sudo apt-get install python3


python-tk:
sudo apt-get install python3-tk


To run the program:
python3 PocketChatV0.5.py

open port 5000 on PocketChip
sudo iptables -A INPUT -p tcp --dport 5000 --jump ACCEPT
sudo iptables-save
