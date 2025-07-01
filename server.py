import socket
IP = "0.0.0.0"
PORT = 80


def main():

    server_socket = socket.socket()
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("server on")
    (proxy_socket, proxy_address) = server_socket.accept()
    print("client on")
    while True:
        data = proxy_socket.recv(1024).decode()
        data_to_proxy = f"{data}"
        proxy_socket.send(data_to_proxy.encode())
        print(data)
        if "EXIT" in data_to_proxy:
            break
    server_socket.close()
    proxy_socket.close()

main()