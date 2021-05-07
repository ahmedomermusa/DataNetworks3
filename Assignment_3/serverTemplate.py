# 
# Import socket library and Hash(MD5) library
#
from socket import *
import hashlib
from os import listdir, path


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

file_ids_to_names = {}  # used in download and upload
file_names_to_ids = {}  # used in list_files

for f in listdir('.\server'):
    file_id = generate_md5_hash(open(".\server\\" + f, 'rb').read())  # this is just temporary
    file_ids_to_names[file_id] = f
    file_names_to_ids[f] = file_id

while True:
    #
    # Accept incoming client connection
    #
    connectSocket, addr = serverSocket.accept()
    print("Client connected: " + str(addr))
    while True:
        request = connectSocket.recv(1024).decode()
        if request == 'LIST_FILES':
            print("LIST_FILES command received")
            print("Listing files..")
            filelist = ["{};{};{}".format(file_names_to_ids[f], f, path.getsize(f)) for i, f in
                        enumerate(listdir('.\server'))]
            if filelist:
                response = '\n'.join(filelist)
                print("Listing files")
            else:
                response = "No files available at the moment."
                print(response)
            connectSocket.send(response.encode())
            connectSocket.send("\n".encode())
            print("Listing files complete")
        elif request == 'DOWNLOAD':
            response = "OK: Waiting for file_id."
            print(response)
            connectSocket.send(response.encode())
            file_id = connectSocket.recv(1024).decode()
            print("OK: file id received :{}".format(file_id))
            if file_id in file_ids_to_names:
                with open(".\server\\" + file_ids_to_names[file_id], 'rb') as file:
                    print("file opened: {}".format(file_ids_to_names[file_id]))
                    print("Sending file..")
                    try:
                        data = file.read(1024)
                        while data:
                            connectSocket.send(data)
                            data = file.read(1024)
                        print("OK: file transfer finished")
                    except:
                        pass
            # Add handling for when file id does not exist\

        elif request == 'UPLOAD':
            print("UPLOAD command received from client")
            response = "OK: Waiting for file data \"file_name;file_size\"."
            print(response)
            connectSocket.send(response.encode())
            file_name, file_size = connectSocket.recv(1024).decode().split(';')
            with open(".\server\\" + file_name, 'wb') as file:
                response = "OK: Ready to receive file"
                print(response)
                connectSocket.send(response.encode())
                endi = int(file_size) // 1024
                i = 0
                while True and i <= endi:
                    i += 1
                    response = connectSocket.recv(1024)
                    if response:
                        file.write(response)
                        continue
                    break
            print("OK: file send complete")
            file_id = generate_md5_hash(open(".\server\\" + file_name, 'rb').read())
            connectSocket.send(file_id.encode())
            print("OK: md5 hash sent")
            if file_name in file_names_to_ids:
                tempid = file_names_to_ids[file_name]
                del file_names_to_ids[file_name]
                del file_ids_to_names[tempid]
            file_ids_to_names[file_id] = file_name
            file_names_to_ids[file_name] = file_id

    # close TCP connection
    connectSocket.close()
