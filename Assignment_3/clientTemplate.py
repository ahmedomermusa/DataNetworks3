# 
# Import socket library and Hash(MD5) library
#
from socket import *
import hashlib
from os import path, listdir
from math import ceil


#
# Generate md5 hash function
#
def generate_md5_hash(file_data):
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
# close TCP connection

def list_files():
    request = 'LIST_FILES'
    print("Listing Files Available on the Server : ")
    clientSocket.send(request.encode())
    responsedict = {}
    result = []
    while True:
        response = clientSocket.recv(1024)
        response = response.decode()
        if response and response != '\n':
            print(response)
            result.append(response)
            continue
        break
    result = ''.join(result)
    result = result.split('\n')
    responsedict = {f.split(';')[0]:tuple(f.split(';')[1:]) for f in result}
    print("Listing files completed")
    print("files_data:", responsedict)
    return responsedict



def download():
    file_id = input("Please Enter The File ID:")
    if file_id not in files_data:
        print("No such file is known.  Use LIST_FILES command (2) to update list of files from server.")
        return
    
    request = 'DOWNLOAD'
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024).decode()
    print("server:" + response)

    file_name = files_data[file_id][0]
    file_size = int(files_data[file_id][1])
    print("Downloading file_id:{}, file_name:{}, file_size:{})".format(file_id, file_name, file_size))
    request = file_id
    with open(".\client\\" + file_name, 'wb') as downloadedfile:
        clientSocket.send(request.encode())
        endi = ceil(file_size/1024)
        i = 0
        while response and i < endi:
            i += 1
            response = clientSocket.recv(1024)
            if response:
                try:
                    downloadedfile.write(response)
                except Exception as e:
                    print(e)
                continue
            break
    md5 = generate_md5_hash(open(".\client\\" + file_name, 'rb').read())
    print("client MD5:", md5)
    if md5 == file_id:
        print("Hashes Matching '\u2713' :Download Success '\u2713' ")
    else:
        print("Download fail: MD5 check failure")


def upload():
    file_name = input("File name:")
    file_size = input("File size:")
    if file_name not in listdir(".\client\\"):
        print("No such file exists.")
        return
    if file_size != path.getsize(".\client\\" + file_name):
        print("Warning!: entered file size is different from actual file size, this may lead to unexpected behavior.")
    request = 'UPLOAD'
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024).decode()
    print("server:" + response)

    # request = "{};{}".format(file_name, path.getsize(".\client\\" + file_name))
    request = "{};{}".format(file_name, file_size)
    clientSocket.send(request.encode())
    response = clientSocket.recv(1024).decode()
    print(response)
    with open(".\client\\" + file_name, 'rb') as file:
        try:
            print("Start sending.....")
            data = file.read(1024)
            while data:
                clientSocket.send(data)
                data = file.read(1024)
        except:
            pass
    # check hash
    response = clientSocket.recv(1024).decode()
    md5 = generate_md5_hash(open(".\client\\" + file_name, 'rb').read())
    print("MD5:", md5)
    print("Hash response from server :", response)
    if md5 == response:
        print("Hashes Matching '\u2713' : Upload success '\u2713' ")
    else:
        print("Upload fail: MD5 check failure")


helpcommands = """1. list files in client directory
2. LIST_FILES from server
3. DOWNLOAD a file from the server (call list files first)
4. UPLOAD a file to a server
"""
print("type help to get list of commands. Commands are numbers only.")

files_data = list_files()  # maps ids to (file_name,file_size)
while True:
    cmd = input("Client>>")
    if cmd == '1':
        print('\n'.join([ "{}:{}".format(f,path.getsize(".\client\\" + f)) for f in listdir(".\client")]))
    elif cmd == '2':
        files_data= list_files()
    elif cmd == '3':
         download()
    elif cmd == '4':
         upload()
    elif cmd == 'help':
        print(helpcommands)

clientSocket.close()
