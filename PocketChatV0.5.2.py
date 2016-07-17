from tkinter import *
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import socket, threading, select, time

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
        
    def init_window(self):# Builds the UI for the main window
        root.title('Python Chat')
        w = 480
        h = 272
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        self.textboxframe = Frame(root)
        self.textboxframe.grid(row=0, column=0, sticky=N+S+E+W)
        Grid.rowconfigure(root, 0, weight=1)
        Grid.columnconfigure(root, 0, weight=1)
        
        self.chatboxframe = Frame(root)
        self.chatboxframe.grid(row=1, column=0, sticky=N+S+E+W)
      
        self.userboxframe = Frame(root)
        self.userboxframe.grid(row=0, column=1, rowspan=2, sticky=N+S+E+W)
 
        self.textReceive = ScrolledText(self.textboxframe,  height=24, width=47, wrap = WORD)
        self.textReceive.grid(row = 0, column= 0, padx=(10,0), pady=(10,5), sticky=N+S+E+W)
        self.textReceive.config(state=DISABLED)
        Grid.rowconfigure(self.textboxframe, 0, weight=1)
        Grid.columnconfigure(self.textboxframe, 0, weight=1)
    
        self.userReceive = Listbox(self.userboxframe, width=12)
        self.userReceive.grid(row = 0, column= 0, padx=(0,10), pady=(10,10), sticky=N+S+E+W)
        Grid.rowconfigure(self.userboxframe, 0, weight=1)
        Grid.columnconfigure(self.userboxframe, 0, weight=1)
        self.userReceive.insert(END, '  Online Users\n')
        
        self.textEntry = ScrolledText(self.chatboxframe, height=2, width=47, wrap = WORD)
        self.textEntry.grid(row = 0, column= 0, padx=(10,0), pady=(0,10), sticky=N+S+E+W)
        Grid.rowconfigure(self.chatboxframe, 0, weight=1)
        Grid.columnconfigure(self.chatboxframe, 0, weight=1)
        self.textEntry.bind('<Return>', self.check_username)
        
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
        
    def iterate_though_message(self, message, user):# If there is a message iterate through it
        e = 0
        char = ''
        for x in message:
            if e >= 6:
                break
            else:
                char += x
                e += 1     
        self.check_for_user_command(message, user, char)
        
    def check_for_user_command(self, message, user, char):# After iterating through the message, check if the message contains any of these commands
        if char == '/nick':
            messagebox.showinfo(message='You must enter a username \n Example: "/nick username"', icon='warning')
            return 'break'
        elif char == '/nick ': 
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
        self.sending(message, user)# If no commands found send message
    
    def send_username_to_server(self, user, usr):# Sends the username to the server and updates the client title to include the new name
        sckt.send(user.encode('utf-8') + ':>/nick '.encode('utf-8') + usr.encode('utf-8'))
        self.textEntry.delete('1.0', END)
        self.master.title('Python Chat - %s' % usr)
        self.aliasname = usr    
        
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
        char = ''
        for j, x in enumerate(data):
            if j < 14:
                char += x 
        if char == '?$@!?*^$&*#@*=':
            self.build_online_list(char, data)
        else:
            self.post_text(data + '\n')    
        
    def build_online_list(self, char, data):# Builds the online users list
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
    
    def post_text(self, post):# Handles the state of the main text box as well as inserting text into the box
        self.textReceive.config(state=NORMAL)
        self.textReceive.insert(END, post)
        self.textReceive.config(state=DISABLED)
        self.textReceive.see(END)
        
root = Tk()
app = Window(root)
root.mainloop()