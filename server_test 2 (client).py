import socket

# user input
name = input('enter your username : ')
bytesToSend1 = str.encode(name)
password = input('enter your password : ')
bytesToSend2 = str.encode(password)

serverAddrPort = ("127.0.0.1", 20001)
bufferSize = 1024

# connecting to hosts
UDPClientSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)

# sending username by encoding it
UDPClientSocket.sendto(bytesToSend1, serverAddrPort)
# sending password by encoding it
UDPClientSocket.sendto(bytesToSend2, serverAddrPort)

# receiving status from server
msgFromServer = UDPClientSocket.recvfrom(bufferSize)
msg = "Message from Server {}".format(msgFromServer[0].decode())
print(msg)