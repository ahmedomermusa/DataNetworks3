# 
# Import socket library and Hash(MD5) library
#
from socket import *
import hashlib
from os import path
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
    clientSocket.send(request.encode())
    responsedict = {}
    while True:
        response = clientSocket.recv(1024).decode()
        if response and response != '\n':
            print(response)
            splitresponse = response.split(';')
            responsedict[splitresponse[0]] = splitresponse[1:]
            continue
        break
    return responsedict


def download(file_id,file_name):
    request = 'DOWNLOAD'
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024).decode()
    print("server:"+response)
    request = file_id
    with open(".\client\\"+file_name,'wb') as downloadedfile:
        clientSocket.send(request.encode())
        while True:
            response = clientSocket.recv(1024)
            if response:
                downloadedfile.write(response)
                continue
            break

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
    #send hash
    response = clientSocket.recv(1024).decode()
    print(response)

    

filelist = list_files()
download("1","The_file.jpg")
upload("The_file.jpg")

clientSocket.close()
