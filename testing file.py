import socket
IP_PROXY = "10.1.58.9"
PORT = 10000


def main():
    # Use a breakpoint in the code line below to debug your script.
    socket.timeout(5)
    my_socket = socket.socket()
    my_socket.connect((IP_PROXY, PORT))

    while True:
        user_input = input("Enter your message")
        my_socket.send(user_input.encode())
        data = my_socket.recv(1024).decode()
        print(f"the data is {data}")
        if user_input == "EXIT":
            break
    my_socket.close()

main()