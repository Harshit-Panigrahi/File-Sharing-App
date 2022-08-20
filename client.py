import socket
from threading import Thread
from tkinter import *
from tkinter import ttk, filedialog

PORT = 8080
IP_ADDRESS = '127.0.0.1'
SERVER = None
BUFFER_SIZE = 4096

name = None
listbox = None
textarea = None
labelchat = None
text_message = None

def openChatWindow():
  window = Tk()
  window.title("Messenger")
  window.geometry("500x350")

  nameLabel = Label(window, text="Enter your Name", font=("Calibri", 10))
  nameLabel.place(x=10, y=10)

  name = Entry(window, width=30, font=("Calibri", 10) )
  name.place(x = 120, y = 10)
  name.focus()

  connectServer = Button(window, text="Connect to Chat Server", font=("Calibri", 10))
  connectServer.place(x = 350, y = 6)

  seperator = ttk.Separator(window, orient="horizontal")
  seperator.place(x=0, y=40, relwidth=1, height=0.1)
  
  labelusers = Label(window, text="Active Users", font=("Calibri", 10))
  labelusers.place(x=20, y=50)

  listbox = Listbox(window, height=5, width=65, font=("Calibri", 10))
  listbox.place(x=20, y=70)
  
  scrollbar1 = Scrollbar(listbox, command=listbox.yview)
  scrollbar1.place(relx=1, relheight=1)

  connectBtn = Button(window, text="Connect", bd=1, font=("Calibri", 10))
  connectBtn.place(x=290, y=160)

  disconnectBtn = Button(window, text="Disconnect", bd=1, font=("Calibri", 10))
  disconnectBtn.place(x=355, y=160)

  refreshBtn = Button(window, text="Refresh", bd=1, font=("Calibri", 10))
  refreshBtn.place(x=430, y=160)

  labelchat = Label(window, text="Chat Window", font=("Calibri", 10))
  labelchat.place(x=20, y=175)

  chatbox = Text(window, height=5, width=65, font=("Calibri", 10))
  chatbox.place(x=20, y=200)

  attachBtn = Button(window, text="Attach & send", bd=1, font=("Calibri", 10))
  attachBtn.place(x=25, y=285)

  chatEntry = Entry(window, width=40, font=("Calibri", 10))
  chatEntry.place(x=120, y=287)

  sendBtn = Button(window, text="Send", bd=1, font=("Calibri", 10))
  sendBtn.place(x=420, y=285)

  window.mainloop()

def setup():
  global SERVER, PORT, IP_ADDRESS

  SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  SERVER.connect((IP_ADDRESS, PORT))

  openChatWindow()

setup()
