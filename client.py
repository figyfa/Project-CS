import socket
IP_PROXY = "127.0.0.1"
PORT = 80


def main():
    # Use a breakpoint in the code line below to debug your script.
    my_socket = socket.socket()
    my_socket.connect((IP_PROXY, PORT))
    data = "0 0"
    while True:
        data = data.split(" ")
        user_input = (f"{str(int(data[0])+1)} {str(data[1])}")
        user_input = ''.join(user_input)
        my_socket.send(user_input.encode())
        data = my_socket.recv(1024).decode()
        print(f"the data is {data}")
        if user_input == "EXIT":
            break
    my_socket.close()

main()