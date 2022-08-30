import socket, ftplib, os, ntpath, time
from threading import Thread
from tkinter import *
from tkinter import ttk, filedialog
from ftplib import FTP
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

PORT = 8080
IP_ADDRESS = '127.0.0.1'
SERVER = None
BUFFER_SIZE = 4096

name = None
sending_file = None
listbox = None
filePathLabel = None
chatbox = None
chatEntry = None

def getFileSize(file_name):
  with open(file_name, "rb") as file:
    chunk = file.read()
    return len(chunk)

def sendMessage():
  global SERVER, chatbox, chatEntry
  msg = chatEntry.get()
  SERVER.send(msg.encode('ascii'))
  chatbox.insert(END, "\nYou: " + msg)
  chatbox.see("end")
  chatEntry.delete(0, 'end')

def receiveMessage():
  global SERVER
  global BUFFER_SIZE
  
  while True:
    chunk = SERVER.recv(BUFFER_SIZE).decode()
    try:
      if("~tiul" in chunk):
        letter_list = chunk.split(",")
        listbox.insert(letter_list[0], letter_list[0]+":"+letter_list[1]+": "+letter_list[3])
      else:
        chatbox.insert(END,"\n"+chunk)
        chatbox.see("end")
    except:
      pass

def connectWithClient():
  global SERVER, listbox
  text = listbox.get(ANCHOR)
  list_items = text.split(":")
  msg = "connect "+ list_items[1]
  SERVER.send(msg.encode('ascii'))

def disconnectWithClient():
  text = listbox.get(ANCHOR)
  list_items = text.split(":")
  msg = "disconnect "+ list_items[1]
  print(msg)
  SERVER.send(msg.encode('ascii'))

def connectToServer():
  global SERVER, name
  global sending_file

  cname = name.get()
  SERVER.send(cname.encode())

def showClientList():
  listbox.delete(0, "end")
  SERVER.send("show list".encode("ascii"))

def browseFiles():
  global chatbox, filePathLabel
  try:
    filename = filedialog.askopenfilename()
    filePathLabel.configure(text=filename)

    HOSTNAME = "127.0.0.1"
    USERNAME = "lftpd"
    PASSWORD = "lftpd"

    ftp_server = FTP(HOSTNAME, USERNAME, PASSWORD)
    ftp_server.encoding = 'utf-8'
    ftp_server.cwd('shared_files')
    fname = ntpath.basename(filename)
    
    with open(filename, 'rb') as file:
      ftp_server.storbinary(f"STOR {fname}", file)
    
    ftp_server.dir()
    ftp_server.quit()

  except FileNotFoundError:
    print("Cancel button has been pressed!...")

def openChatWindow():
  global name, listbox, chatbox, chatEntry, filePathLabel
  window = Tk()
  window.title("Messenger")
  window.geometry("500x350")

  nameLabel = Label(window, text="Enter your Name", font=("Calibri", 10))
  nameLabel.place(x=10, y=10)

  name = Entry(window, width=30, font=("Calibri", 10))
  name.place(x = 120, y = 10)
  name.focus()

  connectServer = Button(window, text="Connect to Chat Server", font=("Calibri", 10), command=connectToServer)
  connectServer.place(x = 350, y = 6)

  seperator = ttk.Separator(window, orient="horizontal")
  seperator.place(x=0, y=40, relwidth=1, height=0.1)
  
  labelusers = Label(window, text="Active Users", font=("Calibri", 10))
  labelusers.place(x=20, y=50)

  listbox = Listbox(window, height=5, width=65, font=("Calibri", 10))
  listbox.place(x=20, y=70)
  
  scrollbar1 = Scrollbar(listbox, command=listbox.yview)
  scrollbar1.place(relx=1, relheight=1)

  connectBtn = Button(window, text="Connect", bd=1, font=("Calibri", 10), command=connectWithClient)
  connectBtn.place(x=290, y=160)

  disconnectBtn = Button(window, text="Disconnect", bd=1, font=("Calibri", 10), command=disconnectWithClient)
  disconnectBtn.place(x=355, y=160)

  refreshBtn = Button(window, text="Refresh", bd=1, font=("Calibri", 10), command=showClientList)
  refreshBtn.place(x=430, y=160)

  chatlabel = Label(window, text="Chat Window", font=("Calibri", 10))
  chatlabel.place(x=20, y=175)

  chatbox = Text(window, height=5, width=65, font=("Calibri", 10))
  chatbox.place(x=20, y=200)

  attachBtn = Button(window, text="Attach & send", bd=1, font=("Calibri", 10))
  attachBtn.place(x=25, y=290)

  chatEntry = Entry(window, width=40, font=("Calibri", 10))
  chatEntry.place(x=120, y=292)

  sendBtn = Button(window, text="Send", bd=1, font=("Calibri", 10), command=sendMessage)
  sendBtn.place(x=420, y=290)

  filePathLabel = Label(window, text="", font=("Calibri", 8))
  filePathLabel.place(x=25, y=320)

  window.mainloop()

def setup():
  global SERVER, PORT, IP_ADDRESS

  SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  SERVER.connect((IP_ADDRESS, PORT))

  recieve_thread = Thread(target=receiveMessage)
  recieve_thread.start()

  openChatWindow()

setup()
