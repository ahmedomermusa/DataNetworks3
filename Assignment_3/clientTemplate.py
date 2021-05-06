# 
# Import socket library and Hash(MD5) library
#
from socket import *
import hashlib
from os import path,listdir
#
# Generate md5 hash function
#
def generate_md5_hash (file_data):
    md5_hash = hashlib.md5(file_data)
    f_id = md5_hash.hexdigest()
    return str(f_id)
# 
# Define Server URL and PORT
#
serverPort = 7700
serverURL = "localhost"
# 
# Create TCP socket for future connections
#
clientSocket = socket(AF_INET, SOCK_STREAM)
# 
# Connect the client to the specified server
#
clientSocket.connect((serverURL, serverPort))
print("Client connected to server: " + serverURL + ":" + str(serverPort))
#
# This client implements the following scenario:
# 1. LIST_FILES
# 2a. UPLOAD the specified file
# 2b. Check MD5
# 3. LIST_FILES
# 4a. DOWNLOAD the previously uploaded file
# 4b. Check MD5
#
#close TCP connection

def list_files():
    request = 'LIST_FILES'
    print("Listing Server Files")
    clientSocket.send(request.encode())
    responsedict = {}
    while True:
        response = clientSocket.recv(1024)
        response = response.decode()
        if response and response != '\n':
            print(response)
            splitresponse = response.split(';')
            responsedict[splitresponse[0]] = tuple(splitresponse[1:])
            continue
        break
    print("Listing files complete")
    return responsedict


def download(file_id,file_name,file_size):
    request = 'DOWNLOAD'
    print("Downloading fileid:{}, file_name:{}, file_size:{})".format(file_id,file_name,file_size))
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024).decode()
    print("server:"+response)
    request = file_id
    with open(".\client\\"+file_name,'wb') as downloadedfile:
        clientSocket.send(request.encode())
        endi = int(file_size)//1024
        i = 0
        while response and i < endi:
            i+=1
            response = clientSocket.recv(1024)
            if response:
                try:
                    downloadedfile.write(response)
                except Exception as e:
                    print(e)
                continue
            break
    md5 = generate_md5_hash(open(".\client\\"+file_name,'rb').read())
    print("MD5:",md5)
    if md5 == file_id:
        print("Download sucess")
    else:
        print("Download fail: MD5 check failure")
        
def upload(file_name):
    request = 'UPLOAD'
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024).decode()
    print("server:"+response)
    request = "{};{}".format(file_name, path.getsize(".\client\\"+file_name))
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024).decode()
    with open(".\client\\"+file_name,'rb') as file:
        try:
            data = file.read(1024)
            while data:
                clientSocket.send(data)
                data = file.read(1024)
        except:
            pass
    #check hash
    response = clientSocket.recv(1024).decode()
    md5 = generate_md5_hash(open(".\client\\"+file_name,'rb').read())
    print("MD5:",md5)
    print("response:",response)
    if md5 == response:
        print("Upload sucess")
    else:
        print("Upload fail: MD5 check failure")
    
helpcommands = """1. list files in client directory
2. LIST_FILES from server
3. DOWNLOAD a file from the server (call list files first)
4. UPLOAD a file to a server
"""
print("type help to get list of commands. Commands are numbers only.")
files_data = {} #maps ids to (file_name,file_size)
while True:
    cmd = input("Client>>")
    if cmd == '1':
        print(listdir(".\client"))
    elif cmd == '2':
        files_data = list_files()
        print("files_data:",files_data)
    elif cmd == '3':
        file_id = input("File ID:")
        file_name = files_data[file_id][0]
        file_size = int(files_data[file_id][1])
        download(file_id, file_name, file_size)
    elif cmd == '4':
        file_name = input("File name:")
        upload(file_name)
    elif cmd == 'help':
        print(helpcommands)

clientSocket.close()
