import os
import sys
import json
import math
import colorsys
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QDialog, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QColor, QPalette

GRID_SIZE = 100  # 100x100 grid
BASE_RADIUS = 5  # base radius in grid cells
ENLARGED_FACTOR = 4  # 4x enlargement on click

# Function to get the application data folder
def get_app_data_folder():
    if sys.platform.startswith("win"):
        appdata = os.getenv('APPDATA')
        folder = os.path.join(appdata, "MyPyQtApp")
    else:
        home = os.path.expanduser("~")
        folder = os.path.join(home, ".config", "MyPyQtApp")
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

# Save and load settings from a json file in the app data folder.
SETTINGS_FILE = os.path.join(get_app_data_folder(), "settings.json")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

# Worker thread that calculates the color gradient.
# It now uses a dynamic dark_color (which cycles with hue) and an adjustable radius.
class GradientWorker(QThread):
    result_ready = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.hover_index = None
        self.running = True
        self.radius = BASE_RADIUS
        # Initialize dark_color with hue corresponding to blue (240°)
        self.dark_color = self.hsv_to_rgb(240 / 360.0, 1.0, 0.78)
        
    def hsv_to_rgb(self, h, s, v):
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))

    def run(self):
        while self.running:
            if self.hover_index is not None:
                i_hover, j_hover = self.hover_index
                grid_colors = []
                for i in range(GRID_SIZE):
                    row = []
                    for j in range(GRID_SIZE):
                        d = math.sqrt((i - i_hover) ** 2 + (j - j_hover) ** 2)
                        if d <= self.radius:
                            factor = max(0, (self.radius - d) / self.radius)
                            # Interpolate from white to the current dark_color
                            r = int(255 + factor * (self.dark_color[0] - 255))
                            g = int(255 + factor * (self.dark_color[1] - 255))
                            b = int(255 + factor * (self.dark_color[2] - 255))
                        else:
                            r, g, b = 255, 255, 255
                        row.append((r, g, b))
                    grid_colors.append(row)
                self.result_ready.emit(grid_colors)
                self.hover_index = None
            self.msleep(10)

    def update_hover(self, index):
        self.hover_index = index

    def stop(self):
        self.running = False
        self.wait()

# Custom widget that displays the grid.
class GridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.grid_colors = [[(255, 255, 255) for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.tile_size = self.width() / GRID_SIZE
        self.worker = GradientWorker()
        self.worker.result_ready.connect(self.handle_result)
        self.worker.start()

        # For cycling the hue on mouse movement (starting at blue: 240°)
        self.hue = 240  

        # Animation variables
        self.animating = False
        self.animation_timer = QTimer(self)
        self.animation_timer.setInterval(20)  # about 50 updates per second
        self.animation_timer.timeout.connect(self.animate_radius)
        self.animation_elapsed = 0
        self.animation_duration = 1000  # in ms
        self.start_radius = BASE_RADIUS
        self.target_radius = BASE_RADIUS * ENLARGED_FACTOR

    def handle_result(self, grid_colors):
        self.grid_colors = grid_colors
        self.update()

    def resizeEvent(self, event):
        self.tile_size = self.width() / GRID_SIZE
        super().resizeEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position() if hasattr(event, 'position') else event.localPos()
        i = int(pos.y() / self.tile_size)
        j = int(pos.x() / self.tile_size)
        if 0 <= i < GRID_SIZE and 0 <= j < GRID_SIZE:
            # Increment hue slightly and wrap around
            self.hue = (self.hue + 1) % 360
            # Update the worker's dark_color using the new hue; using full saturation and 0.78 value for a dark tone
            self.worker.dark_color = self.worker.hsv_to_rgb(self.hue / 360.0, 1.0, 0.78)
            self.worker.update_hover((i, j))
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.animating:
            self.start_enlarge_animation()
        super().mousePressEvent(event)

    def start_enlarge_animation(self):
        self.animating = True
        self.animation_elapsed = 0
        self.animation_timer.start()

    def animate_radius(self):
        # Update elapsed time
        self.animation_elapsed += self.animation_timer.interval()
        t = self.animation_elapsed / self.animation_duration
        # Use sine wave function: sin(pi*t) goes from 0 to 1 (at t=0.5) and back to 0 (at t=1)
        factor = math.sin(math.pi * t)
        self.worker.radius = self.start_radius + (self.target_radius - self.start_radius) * factor

        # Update current hover to trigger redraw if needed
        pos = self.mapFromGlobal(self.cursor().pos())
        i = int(pos.y() / self.tile_size)
        j = int(pos.x() / self.tile_size)
        if 0 <= i < GRID_SIZE and 0 <= j < GRID_SIZE:
            self.worker.update_hover((i, j))

        if self.animation_elapsed >= self.animation_duration:
            self.animation_timer.stop()
            self.worker.radius = BASE_RADIUS  # reset to original radius
            self.animating = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(50, 50, 50))
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                color = self.grid_colors[i][j]
                x = int(j * self.tile_size)
                y = int(i * self.tile_size)
                w = int(self.tile_size)
                h = int(self.tile_size)
                painter.fillRect(x, y, w, h, QColor(*color))

# Help dialog showing program features.
class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help")
        layout = QVBoxLayout()
        help_text = (
            "Features:\n"
            "1. 800x800 window with a 100x100 grid of tiles, each sized as window_width/100.\n"
            "2. The default tile color is white. Hovering over the grid changes the tile's color to a "
            "dynamic dark color that cycles through the spectrum, with nearby tiles blending gradually.\n"
            "3. Clicking on the grid starts an animated expansion of the gradient radius (expands to 4x and returns), "
            "using a sine-wave style animation.\n"
            "4. Multithreading is used for smooth gradient calculations.\n"
            "5. The dark grey aesthetic is maintained across the GUI.\n"
            "6. Settings/data are saved in an app-specific folder (AppData on Windows or ~/.config on Linux).\n"
            "7. The question mark button in the main window opens this help dialog."
        )
        label = QLabel(help_text)
        layout.addWidget(label)
        self.setLayout(layout)

# Main window that includes the grid and a help button.
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid Color Gradient")
        self.setFixedSize(800, 800)
        self.grid_widget = GridWidget(self)
        self.setCentralWidget(self.grid_widget)

        self.help_button = QPushButton("?", self)
        self.help_button.setToolTip("Click for help on features and functionality")
        self.help_button.setFixedSize(30, 30)
        self.help_button.move(self.width() - 40, 10)
        self.help_button.clicked.connect(self.show_help)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(50, 50, 50))
        self.setPalette(palette)

        self.load_gui_settings()

    def show_help(self):
        help_dialog = HelpDialog(self)
        help_dialog.exec()

    def load_gui_settings(self):
        settings = load_settings()
        if "window_geometry" in settings:
            self.restoreGeometry(bytes(settings["window_geometry"], encoding='latin1'))

    def closeEvent(self, event):
        settings = {"window_geometry": self.saveGeometry().toBase64().data().decode('latin1')}
        save_settings(settings)
        self.grid_widget.worker.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
