from tkinter import *
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
import socket, threading, select, time, sys

sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sckt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#server_address = ('127.0.0.1', 5000)
server_address = ('108.61.119.46', 5000)

class Window(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.grid()
        self.online_users = []
        self.aliasname = ''
        self.init_window()
        self.connect_to_server()
        self.pm_tabs = []
        
    def init_window(self):# Builds the UI for the main window
        self.n = ttk.Notebook(root)
        
        self.n.bind_all("<<NotebookTabChanged>>", self.tabChangedEvent)
            
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
        Grid.rowconfigure(root, 0, weight=1)
        Grid.columnconfigure(root, 0, weight=1)  
 
        self.textReceive = ScrolledText(self.textboxframe,  height=24, width=47, wrap = WORD)
        self.textReceive.grid(row = 0, column= 0, padx=(10,0), pady=(10,5), sticky=N+S+E+W)
        self.textReceive.config(state=DISABLED)
        Grid.rowconfigure(self.textboxframe, 0, weight=1)
        Grid.columnconfigure(self.textboxframe, 0, weight=1)
    
        self.userReceive = Listbox(self.textboxframe, width=12)
        self.userReceive.grid(row = 0, column= 1, rowspan=3, padx=(0,10), pady=(10,10), sticky=N+S+E+W)
        Grid.rowconfigure(self.textboxframe, 0, weight=1)
        Grid.columnconfigure(self.textboxframe, 0, weight=1)
        self.userReceive.insert(END, '  Online Users\n')
        
        self.textEntry = ScrolledText(self.textboxframe, height=2, width=47, wrap = WORD)
        self.textEntry.grid(row = 2, column= 0, padx=(10,0), pady=(0,10), sticky=N+S+E+W)
        Grid.rowconfigure(self.textboxframe, 0, weight=1)
        Grid.columnconfigure(self.textboxframe, 0, weight=1)
        self.textEntry.bind('<Return>', self.check_username)
        
        self.n.add(self.textboxframe, text='Chat')
        self.n.grid(row=0, column=0, sticky=N+S+E+W)
        
    def tabChangedEvent(self,event):
        self.current_tab=event.widget.tab(event.widget.index("current"),"text")
        
        
    def connect_to_server(self):# Attemps to connect to the server and starts the receiving thread
        try:
            sckt.connect(server_address)
            thread = threading.Thread(target=self.recv_loop, args=[sckt])
            thread.daemon = True
            thread.start()
            self.getuser_popup()
        except:
            messagebox.showinfo(message='Can\'t connect to the server!\nPlease try again later', icon='warning')
            quit()
            
    def check_username_pm(self, event=None):# Check if they have a username. If they have a username, check if they have a message    
        user = self.aliasname
        message = self.pmEntry.get('1.0','end-1c')
        if user.isspace() or user == '':
            messagebox.showinfo(message='You must enter a username before you can chat', icon='warning')
            return 'break'
        elif message.isspace() or message == '':
            messagebox.showinfo(message='You must enter some text to chat', icon='warning')
            self.pmEntry.delete('1.0', END)
            return 'break'
        for cli in self.online_users:
            if cli in self.current_tab:
                billy = '/msg ' + cli + ' ' + message           
                self.iterate_though_message(billy, user)
                return 'break'    
    
    def check_username(self, event=None):# Check if they have a username. If they have a username, check if they have a message    
        user = self.aliasname
        message = self.textEntry.get('1.0','end-1c')
        if user.isspace() or user == '':
            messagebox.showinfo(message='You must enter a username before you can chat', icon='warning')
            return 'break'
        elif message.isspace() or message == '':
            messagebox.showinfo(message='You must enter some text to chat', icon='warning')
            self.textEntry.delete('1.0', END)
            return 'break'
        self.iterate_though_message(message, user)
        return 'break'
        
    def iterate_though_message(self, message, user):# If there is a message check for / commands
        if message[0] == '/':
            self.check_for_user_command(message, user)
        else:
            self.sending(message, user)# If no / in the first position of the message is found, send the message
            
    def check_for_user_command(self, message, user):# After iterating through the message, check if the message contains any of these commands
        if '/nick ' in message: 
            usr = message.split(' ',1)[1] # Grabs the username after /nick
            if usr == '' or ' ' in usr: # Checks format rules ie. if it contains spaces
                messagebox.showinfo(message='Username cannot contain spaces \n Example: "/nick username"', icon='warning')
                return 'break'
            elif usr in self.online_users:# Checks if the username is taken
                messagebox.showinfo(message='That username is taken.', icon='warning')
                return 'break'              
            else:
                self.send_username_to_server(user, usr)# If the username is not taken, send it to the server  
                return 'break'
        elif '/nick' in message:
            messagebox.showinfo(message='You must enter a username \n Example: "/nick username"', icon='warning')
            return 'break'
        else: 
            if '/msg' in message:
                tabname = message.split(' ',2)
                out_msg = message.split()
                if len(out_msg) >= 3:         
                    self.add_tab_outgoing(tabname[1], user, message)
                else:
                    messagebox.showinfo(message='You must enter some text to chat', icon='warning')
     
    def send_username_to_server(self, user, usr):# Sends the username to the server and updates the client title to include the new name
        sckt.send(user.encode('utf-8') + ':>/nick '.encode('utf-8') + usr.encode('utf-8'))
        self.textEntry.delete('1.0', END)
        self.master.title('Python Chat - %s' % usr)
        self.aliasname = usr

    def sending_pm(self, message, user):# Main sending method. Sends message to server to then be sent to all connected clients
        try:
            sckt.send(user.encode('utf-8')+ ':>'.encode('utf-8') + message.encode('utf-8'))
            self.textEntry.delete('1.0', END)
        except:
            messagebox.showinfo(message='Can\'t send messages while not connected', icon='warning')        
 
    def sending(self, message, user):# Main sending method. Sends message to server to then be sent to all connected clients
        try:
            sckt.send(user.encode('utf-8')+ ':>'.encode('utf-8') + message.encode('utf-8'))
            self.post_text(user + ':>' + message + '\n')
            self.textEntry.delete('1.0', END)
        except:
            messagebox.showinfo(message='Can\'t send messages while not connected', icon='warning')
   
    def recv_loop(self, connection):# The main receiving loop for incoming messages
        while True: 
            (readable, writable, errored) = select.select([connection], [], [connection], 0.1)
            if readable or errored:
                data = connection.recv(1024)
                data = data.decode('utf-8')
                if not data:
                    self.cant_connect()
                self.check_for_commands(data)    
     
    def check_for_commands(self, data):# Looks for a string from the server to start the build_online_list method
        raw_msg = data.split('!',1)
        if data[0] == '?':
            self.build_online_list(data)
        elif data[0] == '!':
            self.post_pm(raw_msg)
            return 'break'
        else:
            self.post_text(data + '\n')    
        
    def post_pm(self, raw_msg):
        send_post = raw_msg[1][0:].split('/msg ')
        send_user = send_post[0].split(':>')
        send_msg = send_post[1].split(self.aliasname + " ")
        done_send = send_user[0] + ':>' + send_msg[1]
        self.add_tab(send_user, done_send)
    
    def add_tab_outgoing(self, send_user, user, done_send):
        for client_id in self.online_users:
            # Check for new Client
            if send_user in client_id and send_user not in self.pm_tabs:
                    # Create Client Tab
                    self.pm_tabs.append(send_user)
                    self.sending_user = send_user
                    self.send_user = self.sending_user + 'frame'
                    self.receive_user = self.sending_user + 'pmReceive'
                    self.pm_Entry = self.sending_user + 'pmSend'
                    self.pm_Close = self.sending_user + 'button'
                    
                    self.send_user= ttk.Frame(self.n)
                    self.send_user.grid(row=0, column=0, rowspan=2, sticky=N+S+E+W)
                    
                    self.receive_user = ScrolledText(self.send_user,  height=24, width=47, wrap = WORD)
                    self.receive_user.grid(row = 0, column= 0, padx=(10,0), pady=(10,5), sticky=N+S+E+W)
                    self.receive_user.config(state=DISABLED)
                    
                    self.pmEntry = ScrolledText(self.send_user, height=2, width=47, wrap = WORD)
                    self.pmEntry.grid(row = 2, column= 0, padx=(10,0), pady=(0,10), sticky=N+S+E+W)
                    self.pmEntry.bind('<Return>', self.check_username_pm)
                    
                    self.pm_Close = Button(self.send_user, width=7, text='Close tab', command=lambda:remove_on_close())
                    self.pm_Close.grid(row = 0, column= 1, padx=(5,5), pady=(5,150), sticky=N+S+E+W)
                    
                    def remove_on_close():
                        self.n.select()
                        self.n.forget(self.n.select())
                        for items in self.pm_tabs:
                            if self.current_tab in items:
                                self.pm_tabs.remove(self.current_tab)
                    
                    Grid.rowconfigure(self.send_user, 0, weight=1)
                    Grid.columnconfigure(self.send_user, 0, weight=1)
                    
                    self.n.add(self.send_user, text = send_user)
                    message = done_send[0:].split(' ',2)
                    self.sending_pm(done_send, user)
                    self.post_pm_controls(user + ':>' + message[2] + '\n')
                    self.n.select(self.send_user)
                    self.pmEntry.delete('1.0', END)
                    self.pmEntry.focus_force()                    
                    
            elif send_user in client_id and send_user in self.pm_tabs:
                if client_id in self.current_tab:
                    message = done_send[0:].split(' ',2)
                    self.sending_pm(done_send, user)
                    self.post_pm_controls(user + ':>' + message[2] + '\n')
                    self.pmEntry.delete('1.0', END)
                    self.pmEntry.focus_force()                    
        
    def add_tab(self, send_user, done_send):
        for client_id in self.online_users:
            # Check for new Client
            if send_user[0] in client_id and send_user[0] not in self.pm_tabs:
                    # Create Client Tab
                    self.pm_tabs.append(send_user[0])
                    self.sending_user = send_user[0]
                    self.send_user = self.sending_user + 'frame'
                    self.receive_user = self.sending_user + 'pmReceive'
                    self.pm_Entry = self.sending_user + 'pmSend'
                    self.pm_Close = self.sending_user + 'button'
                    
                    self.send_user= ttk.Frame(self.n)
                    self.send_user.grid(row=0, column=0, rowspan=2, sticky=N+S+E+W)
                    
                    self.receive_user = ScrolledText(self.send_user,  height=24, width=47, wrap = WORD)
                    self.receive_user.grid(row = 0, column= 0, padx=(10,0), pady=(10,5), sticky=N+S+E+W)
                    self.receive_user.config(state=DISABLED)
                    
                    self.pmEntry = ScrolledText(self.send_user, height=2, width=47, wrap = WORD)
                    self.pmEntry.grid(row = 1, column= 0, padx=(10,0), pady=(0,10), sticky=N+S+E+W)
                    self.pmEntry.bind('<Return>', self.check_username_pm)
                    
                    self.pm_Close = Button(self.send_user, width=7, text='Close tab', command=lambda:remove_on_close())
                    self.pm_Close.grid(row = 0, column= 1, padx=(5,5), pady=(5,150), sticky=N+S+E+W)
                    
                    Grid.rowconfigure(self.send_user, 0, weight=1)
                    Grid.columnconfigure(self.send_user, 0, weight=1)
                    
                    def remove_on_close():
                        self.n.select()
                        self.n.forget(self.n.select())
                        for items in self.pm_tabs:
                            if self.current_tab in items:
                                self.pm_tabs.remove(self.current_tab)
                        
                    self.n.add(self.send_user, text = send_user[0])
                    self.post_pm_controls(done_send + '\n')
                    self.pmEntry.delete('1.0', END)
     
            elif send_user[0] in client_id and send_user[0] in self.pm_tabs:
                self.post_pm_controls(done_send + '\n')
        
    def build_online_list(self, data):# Builds the online users list
        raw_clients = data.split('=',1)[1]
        self.online_users = raw_clients.split(",")
        self.userReceive.delete(1, END)
        for items in self.online_users:
            self.userReceive.insert(END, ' ' + items)
            
    def getuser_popup(self):# Builds the UI for the username entry window 
        self.top = Toplevel()
        self.top.transient(root)
        w = 210
        h = 145
        sw = self.top.winfo_screenwidth()
        sh = self.top.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.top.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        self.enteruser = Entry(self.top, width=18)
        self.enteruser.place(x=32, y=30)
        self.enteruser.focus_force()
        self.enterusername = Label(self.top, text = 'Enter a username to chat')
        self.enterusername.place(x=26, y=5)
        self.changeuser = Label(self.top, text = 'You can change your username\n later by typing /nick in the chat')
        self.changeuser.place(x=3, y=55)
        self.usernameButton = Button(self.top, text='Enter Chat', command = self.get_username, height=2, width=8)
        self.enteruser.bind('<Return>', self.get_username)
        self.usernameButton.place(x=58, y=90)
        
    def get_username(self, event=None):# Gets the initial username after hitting the enter chat button
        self.aliasname = self.enteruser.get()
        if self.aliasname == '':
            messagebox.showinfo(message='You must enter a username', icon='warning')
        elif ' ' in self.aliasname:
            messagebox.showinfo(message='Username cannot contain spaces', icon='warning')
        elif self.aliasname in self.online_users:
            messagebox.showinfo(message='Username is taken.', icon='warning')
        else:
            self.master.title('Python Chat - %s' % self.aliasname)
            sckt.send(self.aliasname.encode('utf-8') + ':>/nick '.encode('utf-8') + self.aliasname.encode('utf-8'))
            self.top.destroy()
            self.textEntry.focus_force()
            
    def post_pm_controls(self, pm):# Handles the state of the tabed text boxs as well as inserting text into the box
        self.receive_user.config(state=NORMAL)
        self.receive_user.insert(END, pm)
        self.receive_user.config(state=DISABLED)
        self.receive_user.see(END)
    
    def post_text(self, post):# Handles the state of the main text box as well as inserting text into the box
        self.textReceive.config(state=NORMAL)
        self.textReceive.insert(END, post)
        self.textReceive.config(state=DISABLED)
        self.textReceive.see(END)
        
root = Tk()
app = Window(root)
root.mainloop()
