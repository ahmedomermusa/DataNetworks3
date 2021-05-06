# 
# Import socket library and Hash(MD5) library
#
from socket import *
import hashlib
from os import listdir, path
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
serverSocket = socket(AF_INET, SOCK_STREAM)
# 
# Bind URL and Port to the created socket
#
serverSocket.bind((serverURL, serverPort))
# 
# Start listening for incoming connection (1 client at a time)
#
serverSocket.listen(1)
print("Server is listening on port: " + str(serverPort))

file_ids_to_names = {} #used in download and upload
file_names_to_ids = {} #used in list_files

i = 0
for f in listdir('.\server'):
    #generate ids using md5
    i += 1
    file_id = str(i) #this is just temporary
    file_ids_to_names[file_id] = f
    file_names_to_ids[f] = file_id

while True:
    # 
    # Accept incoming client connection
    #
    connectSocket, addr = serverSocket.accept()
    print("Client connected: " + str(addr))
    request = connectSocket.recv(1024).decode()
    if request=='LIST_FILES':
        print("Listing files..")
        filelist = [ "{};{};{}".format(file_names_to_ids[f],f, path.getsize(f)) for i,f in enumerate(listdir('.\server'))]
        if filelist:
            response = '\n'.join(filelist)
        else:
            response = "No files available at the moment."
        connectSocket.send(response.encode())
        connectSocket.send("\n".encode())
    elif request == 'DOWNLOAD':
        response = "OK: Waiting for file_id."
        print(response)
        connectSocket.send(response.encode())
        file_id = connectSocket.recv(1024).decode()
        print("file id received :{}".format(file_id))
        if file_id in file_ids_to_names:
            with open(".\server\\"+file_ids_to_names[file_id],'rb') as file:
                print("file opened: {}".format(file_ids_to_names[file_id]))
                try:
                    data = file.read(1024)
                    while data:
                        connectSocket.send(data)
                        data = file.read(1024)
                except:
                    pass
        #Add handling for when file id does not exist\

    elif request == 'UPLOAD':
        response = "OK: Waiting for file data \"file_name;file_size\"."
        print(response)
        connectSocket.send(response.encode())
        file_name,file_size = connectSocket.recv(1024).decode().split(';')
        #generate hash
        with open(".\server\\"+file_name,'wb') as file:
            response = "OK: Ready to receive file"
            print(response)
            connectSocket.send(response.encode())
            endi = int(file_size)//1024
            i = 0
            while True and i < endi:
                i+=1
                print(i)
                response = connectSocket.recv(1024)
                if response:
                    file.write(response)
                    continue
                break
            #receive hash and check
            md5hash = 'GENERATEDHASH' + file_name
            connectSocket.send(md5hash.encode())
            #check md5 hash
            
    #close TCP connection
    connectSocket.close()
