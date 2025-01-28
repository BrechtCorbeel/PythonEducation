import os
import sys
import json
import requests
from PyQt5 import QtCore, QtGui, QtWidgets

"""
PyQt Pokedex using external json from repo: https://github.com/Purukitto/pokemon-data.json
Fix for "QThread: Destroyed while thread is still running" by explicitly stopping threads on close.

Data Flow:
1) Attempts to load local JSON (pokemon.json). If empty/unavailable, fetches from a remote URL.
2) Displays Pokedex style UI with Next/Previous navigation, showing details and a hires image.
3) Threads (QThread) are used for data loading (DataLoader) and image loading (ImageLoader).
4) On closeEvent, all running threads are asked to quit and then waited upon, avoiding QThread errors.
"""

def get_appdata_folder():
    if os.name == 'nt':  # Windows
        appdata = os.getenv('APPDATA')
        if appdata:
            folder_path = os.path.join(appdata, "pokedex_app")
        else:
            folder_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "pokedex_app")
    else:
        folder_path = os.path.join(os.path.expanduser("~"), ".pokedex_app")

    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
    return folder_path

def load_config():
    folder_path = get_appdata_folder()
    config_path = os.path.join(folder_path, "config.json")
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"geometry": "800x600", "last_selected_id": 1}

def save_config(config):
    folder_path = get_appdata_folder()
    config_path = os.path.join(folder_path, "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

class DataLoader(QtCore.QThread):
    dataLoaded = QtCore.pyqtSignal(list)

    def __init__(self, local_path, remote_url):
        super().__init__()
        self.local_path = local_path
        self.remote_url = remote_url
        self._is_interrupted = False

    def run(self):
        data = []
        # Attempt local file
        if os.path.isfile(self.local_path):
            try:
                with open(self.local_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except:
                data = []
        # If none, try remote
        if not data and not self._is_interrupted:
            try:
                resp = requests.get(self.remote_url, timeout=10)
                resp.raise_for_status()
                data = resp.json()
            except:
                data = []
        if not self._is_interrupted:
            self.dataLoaded.emit(data)

    def stop(self):
        self._is_interrupted = True

class ImageLoader(QtCore.QThread):
    imageLoaded = QtCore.pyqtSignal(QtGui.QPixmap, int)

    def __init__(self, url, pokemon_id):
        super().__init__()
        self.url = url
        self.pokemon_id = pokemon_id
        self._is_interrupted = False

    def run(self):
        if self._is_interrupted:
            return
        if not self.url:
            self.imageLoaded.emit(QtGui.QPixmap(), self.pokemon_id)
            return
        try:
            resp = requests.get(self.url, timeout=10)
            resp.raise_for_status()
            if self._is_interrupted:
                return
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(resp.content)
            pixmap = pixmap.scaled(300, 300, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.imageLoaded.emit(pixmap, self.pokemon_id)
        except:
            self.imageLoaded.emit(QtGui.QPixmap(), self.pokemon_id)

    def stop(self):
        self._is_interrupted = True

class PokedexWindow(QtWidgets.QMainWindow):
    def __init__(self, local_json="pokemon.json", remote_json=None):
        super().__init__()
        self.config = load_config()
        self.setMinimumSize(600, 400)

        try:
            w, h = map(int, self.config.get("geometry", "800x600").split('x'))
            self.resize(w, h)
        except:
            self.resize(800, 600)

        self.setWindowTitle("Pokedex")
        self.setStyleSheet("""
            QMainWindow {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 rgba(60, 0, 0, 255), stop:1 rgba(0, 0, 0, 255));
            }
            QTextEdit, QLabel {
                background-color: rgba(0, 0, 0, 100);
                color: white;
            }
            QPushButton {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #660000, stop:1 #990000);
                border-style: outset;
                border-width: 2px;
                border-radius: 6px;
                border-color: #550000;
                color: white;
                font: bold 14px;
                padding: 6px;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
            QComboBox {
                background-color: black;
                color: white;
            }
        """)

        if remote_json is None:
            # Use your provided link or fallback
            remote_json = "https://raw.githubusercontent.com/Purukitto/pokemon-data.json/refs/heads/master/pokedex.json"

        self.pokemon_list = []
        self.current_index = 0
        self.active_threads = []  # Keep references to threads so we can stop them gracefully

        # Layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Navigation bar
        nav_frame = QtWidgets.QFrame()
        nav_layout = QtWidgets.QHBoxLayout()
        nav_frame.setLayout(nav_layout)

        self.prev_button = QtWidgets.QPushButton("Previous")
        self.next_button = QtWidgets.QPushButton("Next")
        self.info_label = QtWidgets.QLabel("Pokédex: 0 / 0")
        self.info_label.setAlignment(QtCore.Qt.AlignCenter)

        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.info_label)
        nav_layout.addWidget(self.next_button)

        main_layout.addWidget(nav_frame)

        # Detail frame
        detail_frame = QtWidgets.QFrame()
        detail_layout = QtWidgets.QHBoxLayout()
        detail_frame.setLayout(detail_layout)
        main_layout.addWidget(detail_frame, 1)

        # Text area
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        detail_layout.addWidget(self.text_edit, 1)

        # Image label
        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        detail_layout.addWidget(self.image_label, 1)

        # Connections
        self.prev_button.clicked.connect(self.show_previous)
        self.next_button.clicked.connect(self.show_next)

        # Start data loading
        self.data_loader = DataLoader(local_json, remote_json)
        self.active_threads.append(self.data_loader)
        self.data_loader.dataLoaded.connect(self.on_data_loaded)
        self.data_loader.start()

    def on_data_loaded(self, data):
        self.pokemon_list = data
        if not self.pokemon_list:
            # No data found
            self.current_index = 0
        else:
            # Attempt to restore last selection
            last_id = self.config.get("last_selected_id", 1)
            found_index = 0
            for idx, poke in enumerate(self.pokemon_list):
                if poke.get("id") == last_id:
                    found_index = idx
                    break
            self.current_index = found_index
        self.update_ui()

    def update_ui(self):
        total = len(self.pokemon_list)
        if total == 0:
            self.info_label.setText("Pokédex: 0 / 0")
            self.text_edit.setText("No Pokémon data found.\n\nCheck local file or remote URL.")
            self.image_label.setPixmap(QtGui.QPixmap())
            return

        self.info_label.setText(f"Pokédex: {self.current_index + 1} / {total}")
        pokemon = self.pokemon_list[self.current_index]
        pid = pokemon.get("id", -1)
        if pid != -1:
            self.config["last_selected_id"] = pid

        name = pokemon.get("name", {}).get("english", "???")
        ptype_list = pokemon.get("type", [])
        ptype_str = ", ".join(ptype_list) if ptype_list else "Unknown"
        species = pokemon.get("species", "Unknown Species")
        description = pokemon.get("description", "No description available.")
        stats = pokemon.get("base", {})
        stats_str = "\n".join(f"{k}: {v}" for k, v in stats.items())

        text = (
            f"Name: {name}\n"
            f"ID: {pid}\n"
            f"Type: {ptype_str}\n"
            f"Species: {species}\n\n"
            f"Base Stats:\n{stats_str}\n\n"
            f"Description:\n{description}\n"
        )
        self.text_edit.setText(text)

        # Load image
        image_url = pokemon.get("image", {}).get("hires", None)
        img_thread = ImageLoader(image_url, pid)
        self.active_threads.append(img_thread)
        img_thread.imageLoaded.connect(self.on_image_loaded)
        img_thread.start()

    def on_image_loaded(self, pixmap, pokemon_id):
        if not self.pokemon_list:
            return
        current_pokemon = self.pokemon_list[self.current_index]
        if current_pokemon.get("id", -1) == pokemon_id:
            self.image_label.setPixmap(pixmap)

    def show_previous(self):
        if not self.pokemon_list:
            return
        self.current_index = (self.current_index - 1) % len(self.pokemon_list)
        self.update_ui()

    def show_next(self):
        if not self.pokemon_list:
            return
        self.current_index = (self.current_index + 1) % len(self.pokemon_list)
        self.update_ui()

    def closeEvent(self, event):
        # Stop and wait for all active threads to finish, preventing the QThread destruction error
        for thr in self.active_threads:
            if thr.isRunning():
                thr.stop()
                thr.quit()
                thr.wait()
        self.config["geometry"] = f"{self.width()}x{self.height()}"
        save_config(self.config)
        super().closeEvent(event)

def main():
    app = QtWidgets.QApplication(sys.argv)
    local_json_path = "pokemon.json"
    remote_json_url = "https://raw.githubusercontent.com/Purukitto/pokemon-data.json/refs/heads/master/pokedex.json"
    window = PokedexWindow(local_json=local_json_path, remote_json=remote_json_url)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
