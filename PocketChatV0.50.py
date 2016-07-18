from tkinter import *
from tkinter.scrolledtext import ScrolledText
import socket, threading, select, time 

sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server_address = ('127.0.0.1', 5000)
server_address = ('108.61.119.46', 5000)

class Window(Frame):
    
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.grid()
        self.init_window()
        
        self.online_users = []
        self.aliasname = ''
        
        self.init_window()
        self.getuser_popup()
       
        sckt.connect(server_address)
        
        thread = threading.Thread(target=self.recv_loop, args=[sckt])
        thread.daemon = True
        thread.start() 

    def init_window(self):
        self.master.title('Python Chat')
        
        w = 480
        h = 272
        sw = self.master.winfo_screenwidth()
        sh = self.master.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        # Makes the frame for the text box that user entry window sits in
        self.textboxframe = Frame(root)
        self.textboxframe.grid(row=0, column=0, sticky=N+S+E+W)
        Grid.rowconfigure(root, 0, weight=1)
        Grid.columnconfigure(root, 0, weight=1)
        
        # Makes the frame for the chat window text from all users
        self.chatboxframe = Frame(root)
        self.chatboxframe.grid(row=1, column=0, sticky=N+S+E+W)
        
        # Make the frame that hold the list of online users
        self.userboxframe = Frame(root)
        self.userboxframe.grid(row=0, column=1, rowspan=2, sticky=N+S+E+W)
        
        # Makes the text box for all messages to be viewed.
        self.textReceive = ScrolledText(self.textboxframe,  height=24, width=47, wrap = WORD)
        self.textReceive.grid(row = 0, column= 0, padx=(10,0), pady=(10,5), sticky=N+S+E+W)
        self.textReceive.config(state=DISABLED)
        Grid.rowconfigure(self.textboxframe, 0, weight=1)
        Grid.columnconfigure(self.textboxframe, 0, weight=1)
        
        # Makes the list box that holds the online users
        self.userReceive = Listbox(self.userboxframe, width=12)
        self.userReceive.grid(row = 0, column= 0, padx=(0,10), pady=(10,10), sticky=N+S+E+W)
        Grid.rowconfigure(self.userboxframe, 0, weight=1)
        Grid.columnconfigure(self.userboxframe, 0, weight=1)
        self.userReceive.insert(END, '  Online Users\n')
        
        # Makes the text entry box for user entry
        self.textEntry = ScrolledText(self.chatboxframe, height=2, width=47, wrap = WORD)
        self.textEntry.grid(row = 0, column= 0, padx=(10,0), pady=(0,10), sticky=N+S+E+W)
        Grid.rowconfigure(self.chatboxframe, 0, weight=1)
        Grid.columnconfigure(self.chatboxframe, 0, weight=1)
        self.textEntry.bind('<Return>', self.sending)
        
    def sending(self, event=None): # All sending functions
        user = self.aliasname # Gets username
        message = self.textEntry.get('1.0','end-1c') # Gets the message
        e = 0
        char = ''
        if message == '': # Checks is there is anything in the message
            self.post_text('You must enter some text to chat.\n')
            return 'break'
            self.sending()
        for x in message: # Iterate through the users message to see if they enter a command, such as /nick
                if e >= 6:
                    break
                else:
                    char += x
                    e += 1
        if user == '': # Check if they have a username
            self.post_text('You must enter a username before you can chat.\n')
            return 'break'
        elif char == '/nick ': # If /nick is in the users message
            usr = message.split(' ',1)[1] # Splits the message and the space
            if usr == '' or usr == ' ': # Checks if user entered anything after /nick
                self.post_text('You must pick a username\n') # Prints if user did'nt enter anything
                return 'break' 
            elif usr in self.online_users: # Checks if the username is in use
                self.post_text('That user name is already taken\n')# Prints if username is taken
                return 'break'              
            else:
                sckt.send(user.encode('utf-8') + ':>/nick '.encode('utf-8') + usr.encode('utf-8'))# If everything above is met we send a message to change username
                self.textEntry.delete('1.0', END)
                self.master.title('Python Chat - %s' % usr)
                self.aliasname = usr # Keeps track of previous username
                char = ''
                return 'break' 
        else: # if were not changing usernames the message will be sent 
            try:
                sckt.send(user.encode('utf-8')+ ':>'.encode('utf-8') + message.encode('utf-8'))
                self.post_text(user + ':>' + message + '\n')
                self.textEntry.delete('1.0', END)

            except:
                self.post_text('Can\'t send messages while not connected.\n')
            return 'break' 
 
    def recv_loop(self, connection):
        while True:
            try:  
                (readable, writable, errored) = select.select([connection], [], [connection], 0.1)
                if readable or errored:
                    data = connection.recv(1024)
                    data = data.decode('utf-8')
                    if not data:
                        print ("Disconnected")
                        return
                    char = ''
                    for j, x in enumerate(data):
                        if j < 14:
                            char += x 
                    if char == '?$@!?*^$&*#@*=':
                        raw_clients = data.split('=',1)[1]
                        self.online_users = raw_clients.split(",")
                        self.userReceive.delete(1, END)
                        for items in self.online_users:
                            self.userReceive.insert(END, ' ' + items)
                    else:
                        self.post_text(data + '\n')
            except:
                self.post_text('Server not responding.\nAttempting to reconnect in 10 seconds...\n')
                time.sleep(10)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(server_address)
                pass
                
    def getuser_popup(self):
        self.top = Toplevel()
        self.top.transient(root)
        w = 210
        h = 160
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
        self.changeuser = Label(self.top, text = 'You can change your username\n later by typing /nick in the chat.')
        self.changeuser.place(x=3, y=55)
        self.usernameButton = Button(self.top, text='Enter Chat', command = self.get_username, height=2, width=8)
        self.enteruser.bind('<Return>', self.get_username)
        self.usernameButton.place(x=58, y=100)
        
    def get_username(self, event=None):
        self.aliasname = self.enteruser.get()
        if self.aliasname == '':
            self.must_enteruser()
            return 'break' 
        elif self.aliasname in self.online_users:
            self.username_taken()
            return 'break'
        else:
            self.master.title('Python Chat - %s' % self.aliasname)
            sckt.send(self.aliasname.encode('utf-8') + ':>/nick '.encode('utf-8') + self.aliasname.encode('utf-8'))
            self.top.destroy()
            self.textEntry.focus_force()
            return 'break' 
            
    def must_enteruser(self):
        self.mustentertop = Toplevel(self.top)
        self.mustentertop.transient(self.top)
        self.mustentertop.lift(self.top)
        w = 225    
        h = 75
        sw = self.mustentertop.winfo_screenwidth()
        sh = self.mustentertop.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.mustentertop.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.mustentertop.transient(root)
        self.mustenter = Label(self.mustentertop, text = 'You must enter a username to chat.')
        self.mustenter.place(x=2, y=5)
        self.okButton = Button(self.mustentertop, text = 'OK', command = self.exit_must_enter, height=2, width=6)
        self.okButton.place(x=73, y=30)
        
    def username_taken(self):
        self.username_takentop = Toplevel(self.top)
        self.username_takentop.transient(self.top)
        self.username_takentop.lift(self.top)
        w = 212    
        h = 75
        sw = self.username_takentop.winfo_screenwidth()
        sh = self.username_takentop.winfo_screenheight()
        x = (sw - w)/2
        y = (sh - h)/2
        self.username_takentop.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.username_takentop.transient(root)
        self.mustenter1 = Label(self.username_takentop, text = 'The username you chose is taken.')
        self.mustenter1.place(x=2, y=5)
        self.okButton1 = Button(self.username_takentop, text = 'OK', command = self.username_taken_exit, height=2, width=6)
        self.okButton1.place(x=73, y=30)
        
    def exit_must_enter(self):
        self.mustentertop.destroy()
        self.top.grab_set()
    
    def username_taken_exit(self):
        self.username_takentop.destroy()
        self.top.grab_set()
    
    def post_text(self, post):
        self.textReceive.config(state=NORMAL)
        self.textReceive.insert(END, post)
        self.textReceive.config(state=DISABLED)
        self.textReceive.see(END)
        
root = Tk()
app = Window(root)
root.mainloop()
