import json
import socket
import threading

import firebase_chat


def register(user_message):
    email = user_message.get("email")
    contact_name = user_message.get("name")
    password = user_message.get("password")

    # Call save_user function
    success = firebase_chat.save_user(email, contact_name, password)

    # Return response to the client
    if success:
        return "User successfully created."
    else:
        return "Failed to create user."

def log_in(user_message):
    email = user_message.get("email")
    password = user_message.get("password")
    logged_in_username, error_message = firebase_chat.verify_user(email, password)
    if logged_in_username:
        print(f"{logged_in_username}is connected")

        user_email = email
        user_chats = firebase_chat.get_user_chats_data(user_email)
        response = json.dumps(user_chats) if user_chats else "No chats found."

        return response # return true because user connected successfully
    else:
        # return error_message
        return "False" # return false because user didn't connect

# Handle client connection
def handle_client(client_socket, client_address):
    print(f"Connection from {client_address}")
    while True:
        try:
            # Receive data from the client
            data = client_socket.recv(1024).decode()
            if data == "QUIT":
                break
            message = json.loads(data)
            type = message.get("type")
            response = ""

            if type == "REGISTER":
                response = register(message)
            elif type == "LOGIN":
                response = log_in(message)
            elif type == "TEXT":
                print(f"{message}")
                firebase_chat.append_message_to_chat(message.get("chat_id"), message.get("text"), message.get("sender_email"))
                response = "message was sent"
            elif type == "TEXT_NEW_CHAT":
                print(f"{message}")

                users = message.get("users")  # Should be a list like ["user1", "user2"]
                if isinstance(users, str):
                    users = json.loads(users)  # Convert string to list if needed

                new_chat_id = firebase_chat.append_message_to_chat(None , message.get("text"), users[0], message.get("users"))

                # firebase_chat.save_chat_history(users, message.get("text"))

                response = f"new chat id: {new_chat_id}"
            else:
                response = "Invalid request type"

        except Exception as e:
            response = f"Error processing request: {e}"

    # Send response back to the client
        client_socket.send(response.encode())
    client_socket.close()

# Start the server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5000))  # Bind to all available interfaces on port 5000
    server_socket.listen(5)
    print("Server is listening on port 5000...")

    while True:
        client_socket, client_address = server_socket.accept()
        # Create a new thread for each client connection
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

# Run the server
if __name__ == "__main__":
    start_server()