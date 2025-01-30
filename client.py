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
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 5000))  # Connect to the server


def login():

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

    if response == "False":
        logged_user = {}

    else:
        logged_user = {
            "email" : email
        }

    return response, logged_user


def register():

    email = input("Enter email: ")
    name = input("Enter contact name: ")
    password = input("Enter password: ")

    user_details = {
        "type": "REGISTER",
        "email": email,
        "name": name,
        "password": password
    }
    client_socket.send(json.dumps(user_details).encode())
    response = client_socket.recv(1024).decode()
    print("Server response:", response)

    return response

def send_chat_message(user):

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

def send_new_chat_message(user):

    receiver_mail = input("Please enter the desired mail")
    text = input("Please enter the desired text")


    new_chat = {
        "type": "TEXT_NEW_CHAT",
        "text" : text,
        "users": [user["email"],receiver_mail]
    }

    client_socket.send(json.dumps(new_chat).encode())
    response = client_socket.recv(1024).decode()
    print("Server response:", response)


if __name__ == "__main__":


    action = input("Enter desired action (LOGIN,REGISTER,TEXT, NEW_CHAT, QUIT):  ")

    is_logged_on = False
    current_user = {}

    while action != "QUIT":
        match action:

            case "REGISTER":
                register_result = register()
            case "LOGIN":
                login_result = login()
                is_logged_on = bool(login_result[0])
                current_user = login_result[1]
            case "NEW_CHAT":
                if is_logged_on:
                    send_new_chat_message(current_user)
                else:
                    print("You're not logged in yet, please use LOGIN")

            case "TEXT":

                if is_logged_on:
                    send_chat_message(current_user)
                else:
                    print("You're not logged in yet, please use LOGIN")

        action = input("Enter desired action (LOGIN,REGISTER,TEXT,NEW_CHAT, QUIT):  ")

    client_socket.send("QUIT".encode())
    client_socket.close()