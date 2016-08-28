from tkinter import messagebox
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
import socket, threading, select, time, sys

sckt = socket.socket()
HOST = "irc.freenode.net"
PORT = 6667
CHANNEL = '#nextthingco'

class Window(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.root = master
        self.grid()
        self.online_users = []
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
    
        self.userReceive = Listbox(self.textboxframe, width=12)
        self.userReceive.grid(row = 0, column= 1, rowspan=3, padx=(0,10), pady=(10,10), sticky=N+S+E+W)

        self.userReceive.insert(END, '  Online Users\n')
        
        self.textEntry = ScrolledText(self.textboxframe, height=2, width=47, wrap = WORD)
        self.textEntry.grid(row = 2, column= 0, padx=(10,0), pady=(0,10), sticky=N+S+E+W)
        self.textEntry.bind('<Return>', self.check_user_commands)
        
        Grid.rowconfigure(root, 0, weight=1)
        Grid.columnconfigure(root, 0, weight=1) 
        Grid.rowconfigure(self.textboxframe, 0, weight=1)
        Grid.columnconfigure(self.textboxframe, 0, weight=1)
        
        self.n.add(self.textboxframe, text=CHANNEL)
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
        
        self.usernameButton = Button(self.top, text='Enter Chat', command = self.get_username, height=2, width=8)
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
        elif self.aliasName in self.online_users:
            messagebox.showinfo(message='Username is taken.', icon='warning')
        else:
            self.master.title('Python Chat - %s' % self.aliasName)
            self.start_recv_loop()
            self.top.destroy()
            self.textEntry.focus_force()    
        
    def start_recv_loop(self):
        sckt.connect((HOST, PORT))
        time.sleep(1)        
        sckt.send(bytes("NICK %s\r\n" % self.aliasName, "UTF-8"))
        time.sleep(1)
        sckt.send(bytes("USER %s %s bla :%s\r\n" % (self.IDENT, HOST, self.REALNAME), "UTF-8"))
        thread = threading.Thread(target=self.recv_loop, args=[sckt])
        thread.daemon = True
        thread.start()
        time.sleep(1)
        sckt.send(bytes("JOIN %s\r\n" % CHANNEL, "UTF-8")) 

    def check_user_commands(self, event=None):
        message = self.textEntry.get('1.0','end-1c')
        self.textEntry.delete('1.0', END)
        self.post_text(self.aliasName + ':>' + message + '\n')
        sckt.send(bytes("PRIVMSG %s %s \r\n" % (CHANNEL, message), "UTF-8"))
        return 'break'  
        
    def recv_loop(self, connection):
        while True: 
            (readable, writable, errored) = select.select([connection], [], [connection], 0.1)
            if readable:
                readbuffer = ""
                readbuffer = readbuffer+connection.recv(1024).decode("UTF-8")
                temp = str.split(readbuffer, "\n")
                readbuffer=temp.pop( )      
                for line in temp:
                    line = str.rstrip(line)
                    line = str.split(line)
                    self.iterate_through_incoming(line, connection)
                    
    def iterate_through_incoming(self, line, connection):                
        if(line[1] == '353'): # Looks for NAMES list
            self.build_online_list(line)
        elif(line[1] == '401'): # Returns warning if user/channel doesn't exist
             messagebox.showinfo(message='No such user with nick %s'% line[3], icon='warning')                    
        elif(line[0] == "PING"):# Looks for PING from the server and replies with a PONG
            connection.send(bytes("PONG %s\r\n" % line[1], "UTF-8"))
        elif(line[1] == "PRIVMSG"): # If PRIVMSG is in line[1] position, its a message from a channel or a private message
            self.get_incoming_channel(line)
        elif(line[1] == 'JOIN' and self.aliasName not in line[0]):# If JOIN is line[1], a new user joined the channel
            self.get_join_leave_name(line)                    
        elif(line[1] == 'PART'): # If PART is line[1] a user has left update the online user list
            self.get_join_leave_name(line)
        elif(line[1] == 'NICK'): # If NICK is line[1] a user has changed their name, update the online user list
            self.get_join_leave_name(line)
        # else:
            # a = line 
            # x = " ".join(a[3:]) # Grabbing everything after the 3rd index and joining the message.      
            # self.post_text(x + '\n')    
            
    def get_incoming_channel(self, line):
        sender = ""
        if "#" in line[2]: #Message from channel
            sender = ""    
            incomg_msg = line[0].split('!') # Split the message at the !
            sender += incomg_msg[0].lstrip(":") # Strip the : out
            a = line 
            x = " ".join(a[3:]) # Grabbing everything after the 3rd index and joining the message.      
            self.post_text(sender+':>'+ x.lstrip(':') + '\n')# Post the received text to the window      
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
            #self.add_tab(sender, sender + ':>' + message.lstrip(':') + '\n')    
            
    def name_change(self, sender, line): # If a name change happens, we change it and update the online users list
        new_user = line[2].split(':')    
        self.online_users.remove(sender)
        self.online_users.append(new_user[1])       
        self.userReceive.delete(1, END)
        self.update_online_list()
        self.post_text('User %s is now known as %s' % (sender, new_user[1]) + '\n')

    def get_join_leave_name(self, line):            
        sender = ""    
        incomg_msg = line[0].split('!')
        sender += incomg_msg[0].lstrip(":")
        if(line[1] == 'JOIN'):
            self.add_online_user(sender)        
        elif(line[1] == 'PART'):
            self.remove_online_user(sender)
        elif(line[1] == 'NICK'):
            self.name_change(sender, line)
            
    def add_online_user(self, sender): # Adds users as they join
        self.online_users.append(sender)      
        self.update_online_list()
        self.post_text('User %s has joined the channel' % sender + '\n')        

    def remove_online_user(self, sender): # Remove users as they leave
        self.online_users.remove(sender)            
        self.userReceive.delete(1, END)
        self.update_online_list()
        self.post_text('User %s has left the channel' % sender + '\n')
        
    def update_online_list(self):
        self.userReceive.delete(1, END)          
        for items in self.online_users:
            self.userReceive.insert(END, ' ' + items)
            
    def build_online_list(self, line):# Builds the online users list
        first_user = line[5].replace(':', '')
        self.online_users.append(first_user)
        for item in line[6:]:
            self.online_users.append(item)
        self.update_online_list()   
            
    def post_text(self, post):# Handles the state of the main text box as well as inserting text into the box
        self.textReceive.config(state=NORMAL)
        self.textReceive.insert(END, post)
        self.textReceive.config(state=DISABLED)
        self.textReceive.see(END)
        
if __name__ == '__main__': 
    root = Tk()
    app = Window(root)
    root.mainloop()         
            
