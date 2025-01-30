import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import bcrypt  # For password hashing
# from google.auth import message

# Initialize Firebase
cred = credentials.Certificate("firebase-key.json")  # Replace with your key file
firebase_admin.initialize_app(cred)
db = firestore.client()  # Use Realtime Database or Firestore based on your setup


#
# def get_user_chats(user_email):
#     """
#     Get all chat IDs where the given user email exists in the 'users' field.
#
#     :param user_email: Email of the user to search for.
#     :return: List of chat document IDs.
#     """
#     try:
#         # Query Firestore for chats where 'users' array contains the given email
#         chats_ref = db.collection("chats")
#         query = chats_ref.where("users", "array_contains", user_email)
#         results = query.stream()
#
#         # Extract chat IDs
#         chat_ids = [doc.id for doc in results]
#
#         return chat_ids
#
#     except Exception as e:
#         print(f"Error fetching chats: {e}")
#         return None  # Return None in case of error

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


def get_user_chats_data(user_email):
    """
    Retrieve all chats where the given user exists.

    :param user_email: The email of the user to search for.
    :return: List of dictionaries containing chat ID, users, and messages.
    """
    try:
        # Query Firestore for chats where 'users' array contains the given email
        chats_ref = db.collection("chats")
        query = chats_ref.where("users", "array_contains", user_email)
        results = query.stream()

        # Extract chat data (ID, users, messages)
        user_chats = []
        for doc in results:
            chat_data = doc.to_dict()
            chat_data["chat_id"] = doc.id  # Add the chat ID to the dictionary
            user_chats.append(chat_data)

        return user_chats

    except Exception as e:
        print(f"Error fetching chats: {e}")
        return None  # Return None in case of error


def append_message_to_chat(doc_id, new_message, email, users=None):
    """
    Append a new message to the `messages` array in an existing chat document.
    If `doc_id` is None, create a new chat instead.

    :param doc_id: The ID of the existing Firestore document (or None to create a new chat)
    :param new_message: The message to append (dict with text, sent_date, type, etc.)
    :param email: User's email
    :param users: Optional list of users to update if necessary
    :return: The chat ID (existing or new), or None if failed
    """
    try:
        message_data = {
            "message": new_message,
            "time_sent": datetime.utcnow().isoformat(),
            "user_email": email,
        }

        if doc_id:  # Append to an existing chat
            doc_ref = db.collection("chats").document(doc_id)

            # Get existing users if not provided
            if users is None:
                users = get_chat_users(doc_id)

            if email not in users:
                users.append(email)  # Consider saving by user ID instead of email

            # Update the chat document
            update_data = {
                "messages": firestore.ArrayUnion([message_data]),
                "users": users,
                "last_updated": datetime.utcnow().isoformat(),
            }
            doc_ref.update(update_data)
            print(f"Message appended to chat with document ID: {doc_id}")
            return doc_id

        else:  # Create a new chat
            chat_data = {
                "messages": [message_data],
                "users": [email] if users is None else users + [email] if email not in users else users,
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
            }
            doc_ref = db.collection("chats").add(chat_data)
            new_chat_id = doc_ref[1].id  # Get generated document ID
            print(f"New chat created with document ID: {new_chat_id}")
            return new_chat_id

    except Exception as e:
        print(f"Error handling chat message: {e}")
        return None


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


def get_chat_users(doc_id : str) -> list[str]:
    try:
        doc_ref = db.collection("chats").document(doc_id)
        doc = doc_ref.get()

        # Check if the document exists
        if doc.exists:
            users = doc.to_dict().get("users")

            if users:
                return users
            else:
                return []
        else:
            print(f"Document {doc_id} does not exist.")
            return []


    except Exception as e:
        print(f"Error reading users list from chat {doc_id}: {e}")
        return []
