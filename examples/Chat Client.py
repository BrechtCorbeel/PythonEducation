import sys
import socket
import threading
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, QObject

class Signal(QObject):
    received = pyqtSignal(str)

class ChatClient(QWidget):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.initUI()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # In your client's init method
        self.signal = Signal()
        self.signal.received.connect(self.updateChat)

    def initUI(self):
        self.setWindowTitle('Chat Client')
        self.setGeometry(100, 100, 400, 600)

        self.layout = QVBoxLayout(self)

        self.chatLabel = QLabel('Chat Messages')
        self.layout.addWidget(self.chatLabel)

        self.chatTextEdit = QTextEdit()
        self.chatTextEdit.setReadOnly(True)
        self.layout.addWidget(self.chatTextEdit)

        self.messageLineEdit = QLineEdit()
        self.layout.addWidget(self.messageLineEdit)

        self.sendButton = QPushButton('Send')
        self.sendButton.clicked.connect(self.sendMessage)
        self.layout.addWidget(self.sendButton)

        self.show()
        
    def updateChat(self, message):
        self.chatTextEdit.append(message)

    def connectToServer(self, username, password):
        self.socket.connect((self.host, self.port))
        login_data = json.dumps({'action': 'login', 'username': username, 'password': password})
        self.socket.send(login_data.encode())
        threading.Thread(target=self.receiveMessages, daemon=True).start()


    def receiveMessages(self):
        while True:
            try:
                message = self.socket.recv(1024).decode()
                print(f"Raw message received: {message}")  # Log raw message data
                if message:
                    message_data = json.loads(message)
                    # Handle non-chat type messages like authentication responses
                    if 'response' in message_data:
                        if message_data['response'] == 'authentication_failed':
                            print("Authentication failed. Please check your credentials.")
                            # Update the GUI or take other actions as needed
                            self.signal.received.emit("Authentication failed. Please check your credentials.")
                        continue  # Skip further processing for this message

                    message_type = message_data.get('type')
                    if message_type == 'chat':
                        self.handleChatMessage(message_data)
                    elif message_type == 'system':
                        self.handleSystemMessage(message_data)
                    # Add other message types as needed
                    else:
                        print(f"Unknown message type: {message_type}")
            except Exception as e:
                print(f"Error receiving message: {e}")
                break


    def sendAcknowledgment(self, message_id):
        ack_message = json.dumps({'action': 'ack', 'id': message_id})
        try:
            self.socket.send(ack_message.encode())
        except Exception as e:
            print(f"Error sending acknowledgment: {e}")


    def sendMessage(self):
        message = self.messageLineEdit.text()
        if message:
            # Check if the socket is connected
            try:
                # This is a way to check if the socket is still open
                self.socket.send(json.dumps({'action': 'message', 'message': message}).encode())
                self.messageLineEdit.clear()
            except OSError:
                print("Socket is closed or not valid.")
                return  # Exit the function if the socket is closed
            
    def handleChatMessage(self, message_data):
        sender = message_data.get('sender', 'Unknown')
        timestamp = message_data.get('timestamp', 'Unknown Time')
        content = message_data.get('message', '')  # Make sure this key matches what the server sends
        # Update the chat window with the new message
        self.signal.received.emit(f"{sender} [{timestamp}]: {content}")

        # Send acknowledgment back to the server
        # self.sendAcknowledgment(message_id)

    def handleSystemMessage(self, message_data):
        # Handle system messages, possibly update GUI or log
        content = message_data.get('content', '')
        self.signal.received.emit(f"System: {content}")

    def handleError(self, message_data):
        # Handle error messages, possibly show an error dialog or notification
        content = message_data.get('content', '')
        print(f"Error: {content}")

    def handleNotification(self, message_data):
        # Handle notifications, such as user joined/left, etc.
        content = message_data.get('content', '')
        self.signal.received.emit(f"Notification: {content}")
    


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Configuration - Update with your server's IP, port, username, and password
    server_ip = '127.0.0.1'
    server_port = 12345
    username = 'your_username2'
    password = 'your_password'

    chat_client = ChatClient(server_ip, server_port)
    chat_client.connectToServer(username, password)

    sys.exit(app.exec_())
