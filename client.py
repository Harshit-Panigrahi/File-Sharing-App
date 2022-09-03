import socket, ftplib, os, ntpath, time
from threading import Thread
from tkinter import *
from tkinter import ttk, filedialog
from ftplib import FTP
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pathlib import Path

PORT = 8080
IP_ADDRESS = '127.0.0.1'
SERVER = None
BUFFER_SIZE = 4096

name = None
sending_file = None
downloading_file = None
file_to_download = None
listbox = None
filePathLabel = None
chatlabel = None
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
  if msg.lower() == "y":
    print("Please wait while the file is downloading...")
    chatbox.insert(END, "\nPlease wait while the file is downloading...")
    chatbox.see("end")

    HOSTNAME = "127.0.0.1"
    USERNAME = "lftpd"
    PASSWORD = "lftpd"

    home = str(Path.home())
    download_path = home + '/Downloads'
    ftp_server = ftplib.FTP(HOSTNAME, USERNAME, PASSWORD)
    ftp_server.encoding = 'utf-8'
    ftp_server.cwd('shared_files')
    fname = file_to_download
    local_filename = os.path.join(download_path, fname)
    file = open(local_filename, 'wb')
    ftp_server.retrbinary('RETR '+ fname, file.write)
    ftp_server.dir()
    file.close()
    ftp_server.quit()
    print("File successfully transferred.....")
    chatbox.insert(END, "\nFile successfully downloaded to path: "+ download_path)
    chatbox.see("end")

def receiveMessage():
  global SERVER, BUFFER_SIZE, file_to_download, downloading_file
  
  while True:
    chunk = SERVER.recv(BUFFER_SIZE).decode()
    try:
      if("~tiul" in chunk):
        letter_list = chunk.split(",")
        listbox.insert(letter_list[0], letter_list[0]+":"+letter_list[1]+": "+letter_list[3])
      elif(chunk=="access granted" or chunk=="access denied"):
        chatlabel.configure(text = "")
        chatbox.insert(END, "\n" + chunk)
        chatbox.see("end")
      elif("download?" in chunk):
        chatlabel.configure(text = "")
        downloading_file = chunk.split(" ")[4].strip()
        BUFFER_SIZE = int(chunk.split(" ")[7])
        chatbox.insert(END, "\n" + chunk)
        chatbox.see("end")
        print(chunk)
      elif("Download:" in chunk):
        chatlabel.configure(text = "")
        getfilename = chunk.split(":")
        file_to_download= getfilename[1]
      else:
        chatlabel.configure(text = "")
        chatbox.insert(END, "\n"+chunk)
        chatbox.see("end")
    except:
      print("An exception occurred")
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
  global SERVER, name, sending_file

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

    msg = ("send " + fname)
    if(msg[:4] == "send"):
      print("Please wait......\n")
      chatbox.insert(END, "\nPlease wait......\n")
      chatbox.see(END)
      sending_file = msg[5:]
      file_size = getFileSize("shared_files/"+sending_file)
      final_msg = msg+" "+str(file_size)
      SERVER.send(final_msg.encode())
      chatbox.insert(END, "\nFile Successfuly Sent")

  except FileNotFoundError:
    print("Cancel button has been pressed")

def openChatWindow():
  global name, listbox, chatbox, chatEntry, filePathLabel, chatlabel
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

  attachBtn = Button(window, text="Attach & send", bd=1, font=("Calibri", 10), command=browseFiles)
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
