import socket
from threading import Thread
import time

IP_ADDRESS = '127.0.0.1'
PORT = 8080
BUFFER_SIZE = None
SERVER = None
clients = {}

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

    print(f"Connection established with {client_name}: {addr}")

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
    
def handleMessage(client, msg, name):
  if msg == "show list":
    handleShowList(client)

def handleShowList(client):
  print(f"client: {client}")
  global clients
  counter=0
  
  for c in clients:
    counter += 1
    client_address = clients[c]["address"][0]
    connected_with = clients[c]["connected_with"]
    msg = ""
    
    if(connected_with):
      msg = f"{counter},{c},{client_address},connected with {connected_with},~tiul"
    else:
      msg = f"{counter},{c},{client_address},Available,~tiul"

    time.sleep(1)
    client.send(msg.encode())
    
def setup():
  print("\n\t\t\t FILE SHARING\n")

  # Getting global values
  global PORT, IP_ADDRESS, SERVER

  SERVER  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  SERVER.bind((IP_ADDRESS, PORT))
  SERVER.listen(100)

  print("\t\tListening for incoming connections...\n")

  acceptConnections()

setup_thread=Thread(target=setup)
setup_thread.start()
