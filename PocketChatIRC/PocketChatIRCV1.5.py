#!/usr/bin/python3
from tkinter import messagebox
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
from socket import socket
from select import select
import sys, threading, time

sckt = socket()
SERVER = 'irc.freenode.net'
PORT = 6667

class Window(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.root = master
        self.grid()
        self.tabs = {}
        self.init_window()
        self.getuser_popup()
        
    def init_window(self):# Builds the UI for the main window
        self.n = ttk.Notebook(root)
    
        root.title('Python Chat')
        w = 480
        h = 272
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        self.textboxframe = ttk.Frame(self.n)
        self.textboxframe.grid(row=0, column=0, sticky=N+S+E+W) 
 
        self.textReceive = ScrolledText(self.textboxframe,  height=24, width=47, wrap = WORD)
        self.textReceive.grid(row = 0, column= 0, padx=(10,0), pady=(10,5), sticky=N+S+E+W)
        self.textReceive.config(state=DISABLED)
        
        self.textEntry = ScrolledText(self.textboxframe, height=2, width=47, wrap = WORD)
        self.textEntry.grid(row = 2, column= 0, padx=(10,0), pady=(0,10), sticky=N+S+E+W)
        self.textEntry.bind('<Return>', self.check_user_commands)
        
        Grid.rowconfigure(root, 0, weight=1)
        Grid.columnconfigure(root, 0, weight=1) 
        Grid.rowconfigure(self.textboxframe, 0, weight=1)
        Grid.columnconfigure(self.textboxframe, 0, weight=1)
        
        self.tabs[SERVER] = {}
        self.tabs[SERVER]['onlinelist'] = []
        self.tabs[SERVER]['textbox'] = self.textReceive
        self.tabs[SERVER]['entrybox'] = self.textEntry
        self.tabs[SERVER]['onlineusers'] = ''
        
        self.n.add(self.textboxframe, text=SERVER)
        self.n.grid(row=0, column=0, sticky=N+S+E+W)
        
    def getuser_popup(self):# Builds the UI for the username entry window 
        self.top = Toplevel()
        self.top.transient(root)
        w = 230
        h = 140
        sw = self.top.winfo_screenwidth()
        sh = self.top.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.top.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        self.enterUser = Entry(self.top, width=18)
        self.enterUser.place(x=75, y=10)
        self.enterUser.focus_force()
        self.enterUsername = Label(self.top, text = 'Nickname')
        self.enterUsername.place(x=5, y=10)
        
        self.enterIDENT = Entry(self.top, width=18)
        self.enterIDENT.place(x=75, y=32)
        self.enterIDENTLb = Label(self.top, text = 'Identity')
        self.enterIDENTLb.place(x=5, y=32)
        
        self.enterREALNAME = Entry(self.top, width=18)
        self.enterREALNAME.place(x=75, y=54)
        self.enterREALNAMELb = Label(self.top, text = 'Realname')
        self.enterREALNAMELb.place(x=5, y=54)
        
        self.usernameButton = Button(self.top, text='Connect', command = self.get_username, height=2, width=8)
        self.usernameButton.bind('<Return>', self.get_username)
        self.usernameButton.place(x=70, y=85)
        
    def get_username(self, event=None):# Gets the initial username after hitting the enter chat button
        self.aliasName = self.enterUser.get()
        self.IDENT = self.enterIDENT.get()
        self.REALNAME = self.enterREALNAME.get()
        if self.aliasName == '':
            messagebox.showinfo(message='You must enter a username', icon='warning')
        elif ' ' in self.aliasName:
            messagebox.showinfo(message='Username cannot contain spaces', icon='warning')
        else:
            self.top.destroy()
            self.master.title('Python Chat - %s' % self.aliasName)
            self.start_recv_loop()
            self.textEntry.focus_force()    
        
    def start_recv_loop(self):
        sckt.connect((SERVER, PORT))
        thread = threading.Thread(target=self.recv_loop, args=[sckt])
        thread.daemon = True
        thread.start()
        time.sleep(1)
        sckt.send(bytes("NICK %s\r\n" % self.aliasName, "UTF-8"))
        time.sleep(1)
        sckt.send(bytes("USER %s %s bla :%s\r\n" % (self.IDENT, SERVER, self.REALNAME), "UTF-8"))

    def check_user_commands(self, event=None):   
        message = self.textEntry.get('1.0','end-1c')
        self.textEntry.delete('1.0', END)
        if message[0] == '/':
            if message == '' or message.isspace():
                messagebox.showinfo(message='You must enter some text', icon='warning')
            if '/msg' in message:
                tab = message.split(' ')
                if len(tab) < 3:
                    messagebox.showinfo(message='You must enter some text after /msg username', icon='warning')
                else:
                    self.add_tab(tab[1], self.aliasName + ':>' + tab[2] + '\n')
                    sckt.send(bytes("PRIVMSG %s %s \r\n" % (tab[1], tab[2]), "UTF-8"))     
            elif '/join' in message:
                tab = message.split(' ')
                if len(tab) < 2:
                    messagebox.showinfo(message='You must enter a channel after /join', icon='warning')
                else:            
                    self.tab_generator(tab[1])
            else:
                self.post_text(self.aliasName + ':>' + message + '\n') 
        return 'break' 

    def check_pm_commands(self, event=None):
        send_to = self.n.tab(self.n.select(), "text")
        textboxinc = self.tabs[send_to]['textbox']
        for user in self.tabs:
            if send_to == user:
                message = self.tabs[send_to]['entrybox'].get('1.0','end-1c')
                self.tabs[send_to]['entrybox'].delete('1.0', END)
                self.tabs[send_to]['entrybox'].focus_force()
        if len(message)>=1 and message[0] == '/':
            if '/msg' in message:
                tab = message.split(' ')
                if len(tab) < 3:
                    messagebox.showinfo(message='You must enter some text after /msg username', icon='warning')
                else:
                    self.add_tab(tab[1], self.aliasName + ':>' + tab[2] + '\n')
                    self.tabs[send_to]['entrybox'].delete('1.0', END)
                    sckt.send(bytes("PRIVMSG %s %s \r\n" % (tab[1], tab[2]), "UTF-8"))     
            elif '/join' in message:
                tabname = message.split(' ',2) 
                self.tabs[send_to]['entrybox'].delete('1.0', END)
                self.tab_generator(tabname[1])
            elif '/leave' in message:
                sckt.send(bytes("PART %s\r\n" % send_to, "UTF-8"))
                self.remove_on_close()
        else:
            self.post_pm_controls(self.aliasName + ':>' + message + '\n', textboxinc)# Post the received text to the window              
            sckt.send(bytes("PRIVMSG %s %s \r\n" % (send_to, message), "UTF-8"))       
        return 'break' 
   
    def recv_loop(self, connection): # Main receiving loop for all incoming messages
        while True:
            (readable, writable, errored) = select([connection], [], [connection], 0.1)
            if readable:
                readbuffer=""    
                readbuffer=readbuffer+sckt.recv(1024).decode("UTF-8")
                temp=str.split(readbuffer, "\n")
                readbuffer=temp.pop( )
                for line in temp:
                    line=str.rstrip(line)
                    line=str.split(line)
                    self.iterate_through_incoming(line, connection)
                
    def iterate_through_incoming(self, line, connection): # Look through the incoming messages for info from the server
        try:
            if line[0] == "PING":# Looks for PING from the server and replies with a PONG
                connection.send(bytes("PONG %s\r\n" % line[1], "UTF-8"))
            elif self.aliasName + '!' in line[0]:
                pass
            elif len(line)>=2 and line[1] == '353': # Looks for NAMES list
                self.build_online_list(line)
            elif len(line)>=2 and line[1] == '401': # Returns warning if user/channel doesn't exist
                messagebox.showinfo(message='No such user with nick %s'% line[3], icon='warning')     
            elif len(line)>=2 and line[1] == "PRIVMSG": # If PRIVMSG is in line[1] position, its a message from a channel or a private message
                self.get_incoming_channel(line)
            elif len(line)>=2 and line[1] == 'JOIN' and self.aliasName not in line[0]:# If JOIN is line[1], a new user joined the channel
                self.get_join_leave_name(line)                    
            elif len(line)>=2 and line[1] == 'PART' and self.aliasName not in line[0]: # If PART is line[1] a user has left update the online user list
                self.get_join_leave_name(line)
            elif len(line)>=2 and line[1] == 'NICK': # If NICK is line[1] a user has changed their name, update the online user list
                self.get_join_leave_name(line)
            elif len(line)>=2 and line[1] == 'NOTICE' and line[2] == self.aliasName:
                    get_tab = line[3].split('[')
                    get_tab_finish = get_tab[1].split(']')
                    x = " ".join(line) # Grabbing everything after the 3rd index and joining the message.
                    self.find_window(get_tab_finish[0], x + '\n')         
            elif len(line)>=4 and line[3] in self.tabs:
                    x = " ".join(line[3:]) # Grabbing everything after the 3rd index and joining the message.
                    self.find_window(line[3], x + '\n')         
            else:
                if ':' in line[0]:
                    x = " ".join(line) # Grabbing everything after the 1st index and join the message.
                    self.post_text(x + '\n')
                else:
                    send_to = self.n.tab(self.n.select(), "text")
                    strayusers = [':placeholder', '353', self.aliasName, '=', send_to]
                    for item in line:
                        strayusers.append(item)
                    self.iterate_through_incoming(strayusers, '0.0.0.0')
        except IndexError:
            pass
         
    def get_incoming_channel(self, line):
        sender = ""
        if "#" in line[2]: # Message from channel
            sender = "" # Get the incoming sender   
            incomg_msg = line[0].split('!') # Split the message at the !
            sender += incomg_msg[0].lstrip(":") # Strip the : out
            a = line 
            x = " ".join(a[3:]) # Grabbing everything after the 3rd index and joining the message.
            self.find_window(line[2], sender+':>'+ x.lstrip(':') + '\n') # Post the received text to the window      
        else: # Private message from user
            sender = ""        
            for char in line[0]:
                if(char == '!'):
                    break                
                if(char != ":"):
                    sender += char 
                    size = len(line)
                    i = 3
                    message = ""
                    while(i < size): 
                        message += line[i] + " "
                        i = i + 1
            self.add_tab(sender, sender + ':>' + message.lstrip(':') + '\n')
            
    def add_tab(self, send_user, done_send):
        if send_user not in self.tabs:
            # Create Client Tab
            self.pm_tab_generator(send_user)
            self.find_window(send_user, done_send)
        else:
            self.find_window(send_user, done_send) 
            
    def tab_generator(self, send_user): # Tab generator for joining channels
        # Create channel tab
        self.send_user = ttk.Frame(self.n)
        self.send_user.grid(row=0, column=0, rowspan=2, sticky=N+S+E+W)
        
        self.receive_user = ScrolledText(self.send_user,  height=24, width=47, wrap = WORD)
        self.receive_user.grid(row=0, column=0, padx=(10,0), pady=(10,5), sticky=N+S+E+W)
        self.receive_user.config(state=DISABLED)
        
        self.pm_users_box = Listbox(self.send_user, width=12)
        self.pm_users_box.grid(row = 0, column= 1, rowspan=3, padx=(0,10), pady=(10,10), sticky=N+S+E+W)
        self.pm_users_box.insert(END, '  Online Users\n')
        
        self.pm_Entry = ScrolledText(self.send_user, height=2, width=47, wrap = WORD)
        self.pm_Entry.grid(row=2, column=0, padx=(10,0), pady=(0,10), sticky=N+S+E+W)
        self.pm_Entry.bind('<Return>', self.check_pm_commands)
       
        Grid.rowconfigure(self.send_user, 0, weight=1)
        Grid.columnconfigure(self.send_user, 0, weight=1)
        
        Grid.rowconfigure(self.send_user, 0, weight=1)
        Grid.columnconfigure(self.send_user, 0, weight=1)
        
        self.tabs[send_user] = {}
        self.tabs[send_user]['onlinelist'] = []
        self.tabs[send_user]['textbox'] = self.receive_user
        self.tabs[send_user]['entrybox'] = self.pm_Entry
        self.tabs[send_user]['onlineusers'] = self.pm_users_box
        self.n.add(self.send_user, text = send_user)
        self.n.select(self.send_user)
        self.pm_Entry.focus_force()
        sckt.send(bytes("JOIN %s\r\n" % send_user, "UTF-8"))
        
    def pm_tab_generator(self, send_user): # Tab generator for PMs from users
        # Create PM tab
        self.send_user = ttk.Frame(self.n)
        self.send_user.grid(row=0, column=0, rowspan=2, sticky=N+S+E+W)
        
        self.receive_user = ScrolledText(self.send_user,  height=24, width=47, wrap = WORD)
        self.receive_user.grid(row=0, column=0, padx=(10,0), pady=(10,5), sticky=N+S+E+W)
        self.receive_user.config(state=DISABLED)
        
        self.pm_Entry = ScrolledText(self.send_user, height=2, width=47, wrap = WORD)
        self.pm_Entry.grid(row=2, column=0, padx=(10,0), pady=(0,10), sticky=N+S+E+W)
        self.pm_Entry.bind('<Return>', self.check_pm_commands)
        
        self.tabs[send_user] = {}
        self.tabs[send_user]['onlinelist'] = []
        self.tabs[send_user]['textbox'] = self.receive_user
        self.tabs[send_user]['entrybox'] = self.pm_Entry
        self.tabs[send_user]['onlineusers'] = ''
        
        self.pm_Close = Button(self.send_user, width=7, text='Close tab', command=lambda:self.remove_on_close())
        self.pm_Close.grid(row=0, column=1, padx=(5,5), pady=(5,150), sticky=N+S+E+W)      
        
        Grid.rowconfigure(self.send_user, 0, weight=1)
        Grid.columnconfigure(self.send_user, 0, weight=1)
            
        self.n.add(self.send_user, text = send_user)
        self.n.select(self.send_user)
        self.pm_Entry.focus_force()
        
    def remove_on_close(self): # Get the current active tab and close it on click
        current_tab = self.n.tab(self.n.select(), "text")
        if current_tab in self.tabs:
            self.n.hide(self.n.select())

    def find_window(self, tab, message): # Get the name of the tab so the message get to the correct tab
        for i in self.n.tabs():
            if tab in self.n.tab(i, "text"):
                self.n.tab(i, state='normal') # Does work   
        for user, window in self.tabs.items():
            if tab == user:
                self.post_pm_controls(message, window['textbox'])# Post the received text to the window  
                
    def name_change(self, sender, line): # If a name change happens, we change it and update the online users list
        for user, window in self.tabs.items():
            for users in self.tabs[user]['onlinelist']:
                if self.tabs[user]['onlinelist'] == '':
                    incbox = window['textbox']
                    inclist = user
                    new_user = line[2].split(':')
                    self.post_pm_controls('User %s is now known as %s' % (sender, new_user[1]) + '\n', incbox)
                elif sender in users: 
                    incbox = window['textbox']
                    inclist = user
                    new_user = line[2].split(':')
                    window['onlinelist'].remove(sender)
                    window['onlinelist'].append(new_user[1])   
                    self.update_online_list(inclist)
                    self.post_pm_controls('User %s is now known as %s' % (sender, new_user[1]) + '\n', incbox)

    def get_join_leave_name(self, line): # Gets the name of the user if they join, leave, or change their name
        tab = line[2].split(':')
        sender = ""    
        incomg_msg = line[0].split('!')
        sender += incomg_msg[0].lstrip(":")
        if(line[1] == 'JOIN'):
            self.add_online_user(sender, tab[0])
        elif(line[1] == 'PART'):
            self.remove_online_user(sender, tab[0])
        elif(line[1] == 'NICK'):
            self.name_change(sender, line)
            
    def add_online_user(self, sender, tab): # Adds users as they join
        inctab = self.tabs[tab]['textbox']
        self.tabs[tab]['onlinelist'].append(sender)
        self.update_online_list(tab)
        self.post_pm_controls('User %s has joined the channel' % sender + '\n', inctab)        

    def remove_online_user(self, sender, tab): # Remove users as they leave
        inctab = self.tabs[tab]['textbox']
        try:
            self.tabs[tab]['onlinelist'].remove(sender)          
            self.update_online_list(tab)
            self.post_pm_controls('User %s has left the channel' % sender + '\n', inctab)
        except ValueError: 
            self.update_online_list(tab)
            self.post_pm_controls('User %s has left the channel' % sender + '\n', inctab)
        
    def update_online_list(self, sender):
        if self.tabs[sender]['onlineusers'] == '':
            pass
        else:
            self.tabs[sender]['onlineusers'].delete(1, END)
            for items in self.tabs[sender]['onlinelist']:
                self.tabs[sender]['onlineusers'].insert(END, items + '\n')

    def build_online_list(self, line):# Builds the online users list
        users = []
        first_user = line[5].replace(':', '')
        users.append(first_user)
        for item in line[6:]:      
            self.tabs[line[4]]['onlinelist'].append(item)    
        self.update_online_list(line[4])   
        
    def post_text(self, post):# Handles the state of the main text box as well as inserting text into the box
        self.textReceive.config(state=NORMAL)
        self.textReceive.insert(END, time.strftime("[%I:%M %p]") + post)
        self.textReceive.config(state=DISABLED)
        self.textReceive.see(END)
        
    def post_pm_controls(self, pm, window):# Handles the state of the tabed text boxes as well as inserting text into the box
        window.config(state=NORMAL)
        window.insert(END, time.strftime("[%I:%M %p]") + pm)
        window.config(state=DISABLED)
        window.see(END)           
        
if __name__ == '__main__': 
    root = Tk()
    app = Window(root)
    root.mainloop()                                 