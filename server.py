import socket, time, os
from threading import Thread
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

IP_ADDRESS = '127.0.0.1'
PORT = 8080
BUFFER_SIZE = None
SERVER = None
clients = {}

is_dir_exists = os.path.isdir('shared_files')
if(not is_dir_exists):
  os.makedirs('shared_files')

def acceptConnections():
  global SERVER
  global clients

  while True:
    client, addr = SERVER.accept()
    client_name = client.recv(4096).decode().lower()
    clients[client_name] = {
      "client" : client,
      "address": addr,
      "connected_with": "",
      "file_name": "",
      "file_size": 4096
    }

    print(f"  Connection established with {client_name}: {addr}")
    thread = Thread(target = handleClient, args=(client, client_name))
    thread.start()

def handleClient(client, name):
  global clients
  global BUFFER_SIZE
  global SERVER

  banner1 = "Welcome, you are now connected to the server!\n Click on Refresh button to see all the available users.\n Select the user and click on Connect to start chatting."
  client.send(banner1.encode())

  while True: 
    try:
      BUFFER_SIZE = clients[name]["file_size"]
      chunk = client.recv(BUFFER_SIZE)
      message = chunk.decode().strip().lower()

      if(message):
        print(f"{name}: {message}")
        handleMessage(client, message, name)
    
    except: 
      pass

def handleErrorMessage(client):
  message = '''
  You need to connect with one of the clients first before sending any files. 
  Click on the Refresh button to see all the available clients.
  '''
  client.send(message.encode())

def handleMessage(client, msg, name):
  if msg == "show list":
    handleShowList(client)
  elif msg[:7] == 'connect':
    connectClient(msg, client, name)
  elif msg[:10] == 'disconnect':
    disconnectClient(msg, client, name)
  elif msg[:4] == "send":
    file_name = msg.split(" ")[1]
    file_size = int(msg.split(" ")[2])
    handleSendFile(name, file_name, file_size)
  elif msg.lower("y"):
    grantAccess(name)
  elif msg.lower("n"):
    denyAccess(name)
  else:
    connected = clients[name]["connected_with"]
    if(connected):
      sendTextMessage(name, msg)
    else: 
      handleErrorMessage(client)
  
def sendTextMessage(name, msg):
  global clients 
  other_client_name = clients[name]["connected_with"]
  other_client_socket = clients[other_client_name]["client"]
  final_msg = f"{name}: {msg}" 
  other_client_socket.send(final_msg.encode())

def handleShowList(client):
  global clients
  counter=0
  
  for cli in clients:
    counter += 1
    client_address = clients[cli]["address"][0]
    connected_with = clients[cli]["connected_with"]
    msg = ""
    
    if(connected_with):
      msg = f"{counter},{cli},{client_address},Connected with {connected_with},~tiul"
    else:
      msg = f"{counter},{cli},{client_address},Available,~tiul"

    time.sleep(1)
    client.send(msg.encode())

def grantAccess(name):
  global clients

  other_client_name = clients[name]["connected_with"]
  other_client_socket = clients[other_client_name]["client"]

  msg = "access granted"
  other_client_socket.send(msg.encode())

def denyAccess(name):
  global clients

  other_client_name = clients[name]["connected_with"]
  other_client_socket = clients[other_client_name]["client"]

  msg = "access denied"
  other_client_socket.send(msg.encode())

def handleSendFile(name, file_name, file_size):
  global clients

  clients[name]["file_name"] = file_name
  clients[name]["file_size"] = file_size

  other_client_name = clients[name]["connected_with"]
  other_client_socket = clients[other_client_name]["client"]

  msg = f"\n {name} wants to send {file_name} file with {file_size} size. Do you want to download? (Y/N)"
  other_client_socket.send(msg.encode())
  time.sleep(1)
  msgdown = f"Download:{file_name}"
  other_client_socket.send(msgdown.encode())

def connectClient(msg, client, name):
  global clients

  entered_client_name = msg[8:].strip()
  if(entered_client_name in clients):
    if(not clients[name]["connected_with"]):
      clients[entered_client_name]["connected_with"] = name
      clients[name]["connected_with"] = entered_client_name

      other_client_socket = clients[entered_client_name]["client"]
      
      greet_msg = f"Hello {entered_client_name}, {name} has connected with you!"
      other_client_socket.send(greet_msg.encode())

      msg = f"You are successfully connected with {entered_client_name}!"
      client.send(msg.encode())
    else:
      other_client_name = clients[name]["connected_with"]
      msg = f"You are already connected with {other_client_name}"
      client.send(msg.encode())
    print(msg)
  
def disconnectClient(msg, client, name):
  global clients 

  entered_name = msg[11:].strip()
  print(entered_name)
  if entered_name in clients:
    if clients[name]["connected_with"] == entered_name:
      print("Disconnecting...")
      clients[entered_name]["connected_with"] = ""
      clients[name]["connected_with"] = ""

      other_client = clients[entered_name]["client"]
      other_client.send(f"{name} has disconnected with you.".encode())

      client.send(f"You have disconnected with {entered_name}".encode())
  print(msg)

def setup():
  global SERVER

  SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  SERVER.bind((IP_ADDRESS, PORT))
  SERVER.listen(100)

  print("Listening for incoming connections...\n")

  acceptConnections()

def ftp():
  authorizer = DummyAuthorizer()
  authorizer.add_user("lftpd", "lftpd", ".", perm= "elradfmw")
  handler = FTPHandler
  handler.authorizer = authorizer

  ftp_server = FTPServer((IP_ADDRESS, 21), handler)
  ftp_server.serve_forever()

print("\n\t\t\t~~*** File Sharing ***~~\n")

setup_thread = Thread(target=setup)
setup_thread.start()

ftp_thread = Thread(target=ftp)
ftp_thread.start()
