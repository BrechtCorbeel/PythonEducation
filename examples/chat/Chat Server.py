import sys
import socket
import threading
import json
import datetime
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt5.QtCore import pyqtSignal, QObject
import os


# Global Variables
clients = []
user_data = {}  # To store user data like {username: {'ip': '...', 'port': ..., 'password': '...'}}




def load_or_create_credentials(file_name='credentials.json'):
    # Check if credentials file exists
    if not os.path.exists(file_name):
        # Generate default or random credentials
        default_credentials = {
            'user1': {'password': 'pass1'},
            'user2': {'password': 'pass2'}
            # Add more as needed or generate them randomly
        }
        # Write default credentials to file
        with open(file_name, 'w') as file:
            json.dump(default_credentials, file, indent=4)
        return default_credentials
    else:
        # Load credentials from file
        with open(file_name, 'r') as file:
            return json.load(file)
        
# At the start of your server script, after defining the function
user_data = load_or_create_credentials()

# Signal class for updating the GUI from a different thread
class Signal(QObject):
    signal = pyqtSignal(str)

class ServerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Server GUI')
        self.setGeometry(100, 100, 400, 600)

        self.layout = QVBoxLayout(self)

        self.logLabel = QLabel('Server Logs:')
        self.layout.addWidget(self.logLabel)

        self.logTextEdit = QTextEdit()
        self.logTextEdit.setReadOnly(True)
        self.layout.addWidget(self.logTextEdit)

        self.show()

    def logMessage(self, message):
        self.logTextEdit.append(message)

def client_handler(client_socket, address, gui_signal):
    global clients, user_data
    username = None  # Initialize username to None

    try:
        while True:
            # Receive data from the client
            data = client_socket.recv(1024).decode()
            if not data:
                break

            # Process data (authentication, message broadcasting, etc.)
            data = json.loads(data)
            action = data.get('action')

            if action == 'login':
                username = data.get('username')
                password = data.get('password')

                # Check if username exists
                if username in user_data:
                    # User exists, check password
                    if user_data[username]['password'] == password:
                        # Successful login
                        client_info = {'client': client_socket, 'address': address, 'username': username}
                        clients.append(client_info)
                        gui_signal.signal.emit(f"User {username} authenticated successfully.")
                        client_socket.send(json.dumps({'response': 'login_success'}).encode())
                    else:
                        # Incorrect password for existing user
                        client_socket.send(json.dumps({'response': 'authentication_failed'}).encode())
                else:
                    # Username does not exist, create new user
                    user_data[username] = {'password': password}
                    clients.append({'client': client_socket, 'address': address, 'username': username})
                    gui_signal.signal.emit(f"New user {username} created and authenticated successfully.")
                    client_socket.send(json.dumps({'response': 'login_success'}).encode())

                    # Update credentials file with new user
                    with open('credentials.json', 'w') as file:
                        json.dump(user_data, file, indent=4)

            elif action == 'register':
                new_username = data.get('username')
                new_password = data.get('password')
                
                if new_username not in user_data:
                    user_data[new_username] = {'password': new_password}
                    with open('credentials.json', 'w') as file:
                        json.dump(user_data, file, indent=4)
                    gui_signal.signal.emit(f"New user {new_username} registered.")
                    client_socket.send(json.dumps({'response': 'registration_success'}).encode())
                    
                    # Send welcome message
                    welcome_message = json.dumps({
                        'type': 'chat',
                        'sender': 'Server',
                        'message': f'Welcome {new_username} to the chat!',
                        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    client_socket.send(welcome_message.encode())
                else:
                    client_socket.send(json.dumps({'response': 'registration_failed', 'reason': 'Username already exists'}).encode())

            elif action == 'message' and username:
                message = data.get('message')
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                broadcast_message = json.dumps({'type': 'chat', 'sender': username, 'message': message, 'timestamp': timestamp})

                for client in clients:
                    try:
                        client['client'].send(broadcast_message.encode())
                        print(f"Sent message to {client['username']}")
                    except Exception as e:
                        print(f"Failed to send message to {client['username']} at {client['address']}: {e}")


                gui_signal.signal.emit(f"Message from {username}: {message}")

    except Exception as e:
        gui_signal.signal.emit(f"Error handling client {address}: {e}")
    finally:
        if username:
            gui_signal.signal.emit(f"{username} has disconnected.")
            clients = [client for client in clients if client['client'] != client_socket]
        client_socket.close()
        
        
def handle_client_messages(client_info):
    while True:
        for message in list(client_info['message_queue']):
            try:
                client_info['client'].send(json.dumps(message).encode())
                # Consider adding logic to mark messages as sent but not yet acknowledged
            except Exception as e:
                print(f"Failed to send message to {client_info['username']} at {client_info['address']}: {e}")
        time.sleep(1)


def start_server(gui_signal):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 12345))
    server.listen(5)
    gui_signal.signal.emit("Server started and listening...")

    try:
        while True:
            client_socket, address = server.accept()
            gui_signal.signal.emit(f"Connection from {address}")
            threading.Thread(target=client_handler, args=(client_socket, address, gui_signal)).start()
    except Exception as e:
        gui_signal.signal.emit(f"Server error: {e}")
    finally:
        server.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    server_gui = ServerGUI()

    # Create a signal instance to update the GUI from the server thread
    gui_signal = Signal()
    gui_signal.signal.connect(server_gui.logMessage)

    # Start the server thread
    threading.Thread(target=start_server, args=(gui_signal,), daemon=True).start()

    sys.exit(app.exec_())
