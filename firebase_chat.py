import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import bcrypt  # For password hashing
# from google.auth import message

# Initialize Firebase
cred = credentials.Certificate("firebase-key.json")  # Replace with your key file
firebase_admin.initialize_app(cred)
db = firestore.client()  # Use Realtime Database or Firestore based on your setup

# Save chat history function
def save_chat_history(users, messages):
    """
    Save chat history in Firebase.

    :param users: List of users in the chat
    :param messages: List of messages (dict format)
    :param id: Document ID for the chat (optional, can be None)
    :return: Document ID if successful, None otherwise
    """
    try:
        chat_data = {
            "users": users,
            "messages": messages,
            "last_updated": datetime.utcnow().isoformat()  # ISO format for timestamp
        }

        # # Save data to Firestore
        # if id:
        #     # Update or set document if an ID is provided
        #     doc_ref = db.collection("chats").document(id)
        #     doc_ref.set(chat_data)
        #     print(f"Chat history saved with ID: {id}")
        #     return id
        # else:
            # Auto-generate document ID if no ID is provided
        doc_ref = db.collection("chats").add(chat_data)
        print(f"Chat history saved with auto-generated ID: {doc_ref[1].id}")
        return doc_ref[1].id

    except Exception as e:
        print(f"Error saving chat history: {e}")
        return None



# Function to append a message to an existing chat document
def append_message_to_chat(doc_id, new_message, email ,users=None):
    """
    Append a new message to the `messages` array in an existing chat document.

    :param email: user's email
    :param doc_id: The ID of the existing Firestore document
    :param new_message: The message to append (dict with text, sent_date, type, etc.)
    :param users: Optional list of users to update if necessary
    :return: True if update succeeds, False otherwise
    """
    try:
        doc_ref = db.collection("chats").document(doc_id)

        # Prepare the update data
        update_data = {
            "messages": firestore.ArrayUnion([{"message": new_message, "time sent" : datetime.utcnow().isoformat(), "user email": email}]),
            "last_updated": datetime.utcnow().isoformat(),  # Update timestamp
        }

        # Optionally update users if provided
        if users:
            update_data["users"] = users

        # Perform the update
        doc_ref.update(update_data)
        print(f"Message appended to chat with document ID: {doc_id}")
        return True
    except Exception as e:
        print(f"Error appending message to chat: {e}")
        return False


# Function to hash passwords
def hash_password(password):
    """
    Hash a plaintext password.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()  # Convert bytes to string for storage

# Function to save user details
def save_user(email, contact_name, password):
    """
    Save user details in Firebase.

    :param email: User's email (unique identifier)
    :param contact_name: User's contact name
    :param password: User's password (hashed for security)
    :return: True if user is successfully saved, False otherwise
    """
    try:
        hashed_password = hash_password(password)
        user_data = {
            "email": email,
            "contact_name": contact_name,
            "password": hashed_password,
            "created_at": datetime.utcnow().isoformat(),
        }

        # Save data to Firestore under 'users/<email>'
        db.collection("users").document(email).set(user_data)
        print(f"User details saved for email: {email}")
        return True
    except Exception as e:
        print(f"Error saving user: {e}")
        return False


def check_send_message_to_fb():
    users = ["Alice", "Bob"]
    messages = [
        {
            "text": "Hello, Bob!",
            "sent_date": datetime.utcnow().isoformat(),
            "type": "text"
        },
        {
            "text": "Hi Alice! Here's an image.",
            "sent_date": datetime.utcnow().isoformat(),
            "type": "img"
        },
        {
            "text": "Check this audio message.",
            "sent_date": datetime.utcnow().isoformat(),
            "type": "audio"
        }
    ]
    save_chat_history(users, messages)

def check_add_user():
    # Example to save a user
    email = "user@example.com"
    contact_name = "John Doe"
    password = "securepassword123"

    save_user(email, contact_name, password)


# Function to verify user credentials
def verify_user(email, password):
    """
    Verify user credentials.

    :param email: User's email
    :param password: Plaintext password to check
    :return: contact_name if the credentials are correct, None otherwise
    """
    # Retrieve the user document
    user_ref = db.collection("users").document(email)
    user_doc = user_ref.get()

    if not user_doc.exists:
        print("User not found.")
        return None, "User not found."

    user_data = user_doc.to_dict()
    stored_hashed_password = user_data["password"]

    # Check if the provided password matches the stored hashed password
    if bcrypt.checkpw(password.encode(), stored_hashed_password.encode()):
        print(f"User verified: {user_data['contact_name']}")
        return user_data["contact_name"], "Correct Password"
    else:
        print("Incorrect password.")
        return None, "Incorrect password."

def check_verify():
    # Example to verify user
    verified_name = verify_user("user@example.com", "securepassword123")
    if verified_name:
        print(f"Welcome, {verified_name}!")
    else:
        print("Invalid credentials.")


# check_add_user()
# check_verify()
# save_chat_history(['user'],'text','123')