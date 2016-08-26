import select, socket, time

# Set up the listening socket
sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sckt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sckt.bind(('0.0.0.0', 5000))
sckt.listen(10)
sckt.setblocking(0)
connections = []
usrList = {}
connections.append(sckt)

def online_clients():
    try:
        online_users = '?$@!?*^$&*#@*='
        for x in usrList.keys():
            online_users += (x + ',')
        for socket in connections:
            if socket != sckt:
                time.sleep(0.1)
                socket.send(online_users.encode('utf-8'))
    except:
        pass

def send_all(message):
    try:
        for socket in connections:
            if socket != sckt and socket != sock:
                time.sleep(0.5)
                socket.send(message.encode('utf-8'))
    except:
        pass

def send_pm(message, user):
    usr = message.split(' ',2)[1]
    for socket in connections:
        if usrList[usr] == socket and usrList[user] != socket:
            socket.send('!'.encode('utf-8') + message.encode('utf-8'))
          
def send_self(alert):
    try:
        for socket in connections:
            if socket != sckt and socket == sock:
                socket.send(alert.encode('utf-8'))
    except:
        pass
        
def iterate_through_message(message, sock):# check through the messages for / commands
    user, raw_msg = message.split(':>',1)
    if raw_msg[0] == '/':
        check_for_user_commands(user, message, raw_msg, sock)      
    else:
        send_all(message)

def check_for_user_commands(user, message, raw_msg, sock):
# If / is found routes to method of user command      
    if '/nick' in raw_msg:
        check_username(user, raw_msg, sock)
    elif '/msg' in raw_msg:
        send_pm(message, user)
 
def check_username(user, raw_msg, sock):# Check if the username is 
    usr = raw_msg.split(' ',1)[1]
    # is the username is in the dic it del the user
    if usr in usrList.keys():
        send_self('The user name you requested is already taken')
    if user in usrList.keys(): #and list(usrList.keys())[list(usrList.values()).index(sock)] == usr:
        del usrList[user]
        usrList[usr] = sock
        send_all('User %s is now known as %s' % (user, usr))
        time.sleep(0.3)
        online_clients()
    # If the username is not in the dic and is joining the first time
    else:
        usrList[usr] = sock
        send_all('User %s has joined the chat' % usr)
        time.sleep(0.4)
        online_clients()                
        
def remove_disconnected_client(sock):# Remove disconnected clients
    try:
        a = list(usrList.keys())[list(usrList.values()).index(sock)]
        del usrList[a]
        connections.remove(sock)
        online_clients()
        time.sleep(0.6)
        send_all('User %s has left the chat' % a)
        print('User %s has left the chat' % a)
    except:
        print('User left before entering a name and joining the chat.')
        connections.remove(sock)
        online_clients()
        pass             
        
# We must accept connections in a loop
while True:
    print ("Waiting for any change")
    readable, writable, errored = select.select(connections, [], [])
    for sock in readable:
        # If it's the main socket, then it's a new connection, otherwise it's a new message
        if sock == sckt:
            connection, address = sckt.accept()
            connections.append(connection)
            print ("New connection received from %s" % str(address))
            online_clients()
        else:
            # A message has been sent to us or the connection is closed
            try:
                message = sock.recv(1024)
                message = message.decode('utf-8')
                if not message:
                    remove_disconnected_client(sock)
                else:
                    iterate_through_message(message, sock)
            except:
                remove_disconnected_client(sock)
                
 
        
                               