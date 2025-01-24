import socket
import json

from pyasn1.type.univ import Boolean


# Function to send user data to the server
# def send_user_data(email, contact_name, password, action):
#
#
#     # Create user data as JSON
#     user_details = {
#         "type": action,
#         "email": email,
#         "contact_name": contact_name,
#         "password": password
#     }
#     client_socket.send(json.dumps(user_details).encode())
#
#     # Receive response from the server
#     response = client_socket.recv(1024).decode()
#     print("Server response:", response)
#     client_socket.close()

def login():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 5000))  # Connect to the server

    email = input("Enter email: ")
    # contact_name = input("Enter contact name: ")
    password = input("Enter password: ")

    user_details = {
        "type": "LOGIN",
        "email": email,
        # "contact_name": contact_name,
        "password": password
    }
    client_socket.send(json.dumps(user_details).encode())
    response = client_socket.recv(1024).decode()
    print("Server response:", response)

    if response == "True":
        logged_user = {
            "email" : email
        }
    else:
        logged_user = {}

    return response, logged_user

def send_chat_message(user):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 5000))  # Connect to the server

    chat_id = input("Please enter the desired chat")
    text = input("Please enter the desired text")


    new_chat = {
        "type": "TEXT",
        "chat_id" : chat_id,
        "text" : text,
        "sender_email": user["email"]
    }

    client_socket.send(json.dumps(new_chat).encode())
    response = client_socket.recv(1024).decode()
    print("Server response:", response)

if __name__ == "__main__":


    action = input("Enter desired action (LOGIN,REGISTER,TEXT,QUIT):  ")

    is_logged_on = False
    current_user = {}

    while action != "QUIT":
        match action:
            case "LOGIN":
                login_result = login()
                is_logged_on = bool(login_result[0])
                current_user = login_result[1]
            case "TEXT":

                if is_logged_on:
                    send_chat_message(current_user)
                else:
                    print("You're not logged in yet, please use LOGIN")

        action = input("Enter desired action (LOGIN,REGISTER,TEXT,QUIT):  ")

