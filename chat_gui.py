import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QLabel,
    QTextEdit, QPushButton, QListWidgetItem, QScrollArea
)
from PyQt6.QtCore import Qt
from firebase_chat import get_user_chats_data  # Import your Firebase function

USER_EMAIL = "hodaya"  # Replace with actual logged-in user email

class ChatApp(QWidget):
    def __init__(self):
        super().__init__()

        # Main Layout
        self.setWindowTitle("Chat Application")
        self.setGeometry(100, 100, 800, 600)
        layout = QHBoxLayout(self)

        # Right Side (Chat List)
        self.chat_list = QListWidget()
        # each time you  click on chat in left side, call load_chat function
        self.chat_list.itemClicked.connect(self.load_chat)
        layout.addWidget(self.chat_list, 3)  # 3:7 ratio

        # Left Side (Chat View)
        self.chat_view = QWidget()
        chat_layout = QVBoxLayout(self.chat_view)

        # Chat Users
        self.chat_users_label = QLabel("Users in Chat:")
        chat_layout.addWidget(self.chat_users_label)

        # Messages Area
        self.message_area = QListWidget()
        chat_layout.addWidget(self.message_area)

        # Message Input
        self.message_input = QTextEdit()
        chat_layout.addWidget(self.message_input)

        # Send Button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        chat_layout.addWidget(self.send_button)

        layout.addWidget(self.chat_view, 7)  # 7:10 ratio

        self.load_chat_list()  # Load available chats

    def load_chat_list(self):
        """ Load chat IDs into the chat list. """
        self.chats = get_user_chats_data(USER_EMAIL)
        if self.chats:
            for chat in self.chats:
                chat_id = chat["chat_id"]
                item = QListWidgetItem(chat_id)
                item.setData(Qt.ItemDataRole.UserRole, chat)  # Store chat data
                self.chat_list.addItem(item)

    def load_chat(self, item):
        """ Load selected chat messages and users. """
        chat_data = item.data(Qt.ItemDataRole.UserRole)

        # Update chat users
        self.chat_users_label.setText(f"Users: {', '.join(chat_data['users'])}")

        # Load messages
        self.message_area.clear()
        for msg in chat_data.get("messages", []):
            sender = msg.get("user email", "Unknown")
            text = msg.get("message", "")
            self.message_area.addItem(f"{sender}: {text}")

    def send_message(self):
        """ Send a message (This function will be connected to Firebase later). """
        text = self.message_input.toPlainText()
        if text.strip():
            self.message_area.addItem(f"You: {text}")
            self.message_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec())
