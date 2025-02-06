import sys
import os
import json
import math
import numpy as np
import sympy as sp
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QLocale
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, QGridLayout,
    QLabel, QVBoxLayout, QHBoxLayout, QSlider, QGroupBox, QSplitter
)
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.collections import LineCollection
import matplotlib.colors as mcolors

# ---------------- Appdata Setup ----------------

def get_appdata_folder():
    if os.name == 'nt':
        base_dir = os.getenv('APPDATA')
        folder = os.path.join(base_dir, "UltraAdvancedCalculator")
    else:
        home = os.path.expanduser("~")
        folder = os.path.join(home, ".ultra_advanced_calculator")
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

STATE_FILE = os.path.join(get_appdata_folder(), "state.json")

# ---------------- Advanced Calculation Functions ----------------

def diff_func(expr, var='x'):
    try:
        var_sym = sp.symbols(var)
        return str(sp.diff(sp.sympify(expr), var_sym))
    except Exception:
        return "Error"

def integrate_func(expr, var='x'):
    try:
        var_sym = sp.symbols(var)
        return str(sp.integrate(sp.sympify(expr), var_sym))
    except Exception:
        return "Error"

def simplify_func(expr):
    try:
        return str(sp.simplify(sp.sympify(expr)))
    except Exception:
        return "Error"

def factor_func(expr):
    try:
        return str(sp.factor(sp.sympify(expr)))
    except Exception:
        return "Error"

def expand_func(expr):
    try:
        return str(sp.expand(sp.sympify(expr)))
    except Exception:
        return "Error"

# Allowed names for direct evaluation
ALLOWED_NAMES = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "sqrt": math.sqrt,
    "factorial": math.factorial,
    "pi": math.pi,
    "e": math.e,
    "abs": abs,
    "round": round,
    "pow": pow,
    # Symbolic functions:
    "diff": diff_func,
    "integrate": integrate_func,
    "simplify": simplify_func,
    "factorize": factor_func,
    "expand": expand_func
}

# Allowed names for graph evaluation using numpy
ALLOWED_NAMES_GRAPH = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "arcsin": np.arcsin,
    "arccos": np.arccos,
    "arctan": np.arctan,
    "sinh": np.sinh,
    "cosh": np.cosh,
    "tanh": np.tanh,
    "log": np.log,
    "log10": np.log10,
    "exp": np.exp,
    "sqrt": np.sqrt,
    "pi": np.pi,
    "e": np.e,
    "abs": np.abs,
    "round": np.round,
    "power": np.power,
    "np": np
}

# ---------------- Thread Classes ----------------

class EvaluationThread(QThread):
    result_signal = pyqtSignal(object)

    def __init__(self, expression, allowed_names):
        super().__init__()
        self.expression = expression
        self.allowed_names = allowed_names

    def run(self):
        try:
            expr = self.expression.replace("^", "**")
            result = eval(expr, {"__builtins__": None}, self.allowed_names)
        except Exception:
            result = "Error"
        self.result_signal.emit(result)

class GraphThread(QThread):
    plot_signal = pyqtSignal(np.ndarray, np.ndarray)
    error_signal = pyqtSignal(str)

    def __init__(self, expression, lower, upper, num_points=1000):
        super().__init__()
        self.expression = expression
        self.lower = lower
        self.upper = upper
        self.num_points = num_points

    def run(self):
        try:
            x = np.linspace(self.lower, self.upper, self.num_points)
            expr = self.expression.replace("^", "**")
            local_dict = {"x": x}
            local_dict.update(ALLOWED_NAMES_GRAPH)
            y = eval(expr, {"__builtins__": None}, local_dict)
            if not isinstance(y, np.ndarray):
                y = np.full_like(x, y)
            self.plot_signal.emit(x, y)
        except Exception as e:
            self.error_signal.emit("Error: " + str(e))

# ---------------- Gradient Line Plotting ----------------

def gradient_line(ax, x, y, cmap_name="viridis"):
    """
    Plot a line with a gradient color.
    """
    # Create line segments for coloring
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    norm = plt.Normalize(x.min(), x.max())
    cmap = plt.get_cmap(cmap_name)
    lc = LineCollection(segments, cmap=cmap, norm=norm)
    # Set the values used for colormapping
    lc.set_array(x)
    lc.set_linewidth(2)
    line = ax.add_collection(lc)
    ax.autoscale_view()
    return line

# We need to import pyplot from matplotlib here for normalization and colormaps.
import matplotlib.pyplot as plt

# ---------------- Calculator and Graph Integrated Widget ----------------

class IntegratedCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.eval_thread = None
        self.graph_thread = None
        self.init_ui()
        self.load_state()

    def init_ui(self):
        self.setWindowTitle("Ultra Advanced Scientific Calculator")
        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit {
                background-color: #3e3e3e;
                color: #ffffff;
                border: 1px solid #555555;
                padding: 4px;
            }
            QPushButton {
                background-color: #4e4e4e;
                color: #ffffff;
                border: none;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #6e6e6e;
            }
            QLabel {
                padding: 4px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #3A3939;
                height: 8px;
                background: #4e4e4e;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #6e6e6e;
                border: 1px solid #3A3939;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)

        # ----- Calculator Group -----
        calc_group = QGroupBox("Calculator")
        calc_layout = QVBoxLayout()

        self.calc_input = QLineEdit()
        self.calc_input.setPlaceholderText("Enter expression (e.g., sin(pi/2)+3^2)")
        self.calc_result = QLabel("")

        # Keypad grid
        keypad = QGridLayout()
        buttons = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2), ("/", 0, 3),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2), ("*", 1, 3),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2), ("-", 2, 3),
            ("0", 3, 0), (".", 3, 1), ("(", 3, 2), (")", 3, 3),
            ("+", 4, 0), ("^", 4, 1), ("sqrt", 4, 2), ("exp", 4, 3),
            ("sin", 5, 0), ("cos", 5, 1), ("tan", 5, 2), ("log", 5, 3),
            ("diff", 6, 0), ("integrate", 6, 1), ("simplify", 6, 2), ("expand", 6, 3),
            ("C", 7, 0), ("DEL", 7, 1), ("=", 7, 2, 1, 2)
        ]
        self.button_mapping = {
            "sqrt": "sqrt(",
            "exp": "exp(",
            "sin": "sin(",
            "cos": "cos(",
            "tan": "tan(",
            "log": "log(",
            "diff": "diff(",
            "integrate": "integrate(",
            "simplify": "simplify(",
            "expand": "expand("
        }
        for btn_def in buttons:
            if len(btn_def) == 3:
                text, row, col = btn_def
                rowspan, colspan = 1, 1
            else:
                text, row, col, *span = btn_def
                if len(span) == 1:
                    rowspan, colspan = span[0], 1
                else:
                    rowspan, colspan = span
            btn = QPushButton(text)
            btn.clicked.connect(lambda _, t=text: self.on_calc_button(t))
            keypad.addWidget(btn, row, col, rowspan, colspan)

        calc_layout.addWidget(self.calc_input)
        calc_layout.addWidget(self.calc_result)
        calc_layout.addLayout(keypad)

        # Buttons for calculating and plotting from the calculator input
        action_layout = QHBoxLayout()
        self.calculate_btn = QPushButton("Calculate")
        self.calculate_btn.clicked.connect(self.calculate_expression)
        self.plot_btn = QPushButton("Graph Function")
        self.plot_btn.clicked.connect(self.plot_from_calc)
        action_layout.addWidget(self.calculate_btn)
        action_layout.addWidget(self.plot_btn)
        calc_layout.addLayout(action_layout)
        calc_group.setLayout(calc_layout)

        # ----- Graph Group -----
        graph_group = QGroupBox("Graph Plotter")
        graph_layout = QVBoxLayout()

        # Function expression field (pre-filled from calc_input if possible)
        self.graph_expr = QLineEdit()
        self.graph_expr.setPlaceholderText("Enter function f(x), e.g., sin(x)+x^2")
        # Boundary fields and sliders in a horizontal layout
        bound_layout = QHBoxLayout()

        self.lower_field = QLineEdit()
        self.lower_field.setPlaceholderText("Lower bound")
        self.lower_field.setValidator(QDoubleValidator())
        self.upper_field = QLineEdit()
        self.upper_field.setPlaceholderText("Upper bound")
        self.upper_field.setValidator(QDoubleValidator())

        self.lower_slider = QSlider(Qt.Orientation.Horizontal)
        self.lower_slider.setMinimum(-1000)
        self.lower_slider.setMaximum(1000)
        self.lower_slider.setValue(-10)
        self.upper_slider = QSlider(Qt.Orientation.Horizontal)
        self.upper_slider.setMinimum(-1000)
        self.upper_slider.setMaximum(1000)
        self.upper_slider.setValue(10)

        # Sync sliders and fields
        self.lower_slider.valueChanged.connect(self.sync_lower_field)
        self.upper_slider.valueChanged.connect(self.sync_upper_field)
        self.lower_field.editingFinished.connect(self.sync_lower_slider)
        self.upper_field.editingFinished.connect(self.sync_upper_slider)

        bound_layout.addWidget(QLabel("Lower:"))
        bound_layout.addWidget(self.lower_field)
        bound_layout.addWidget(self.lower_slider)
        bound_layout.addWidget(QLabel("Upper:"))
        bound_layout.addWidget(self.upper_field)
        bound_layout.addWidget(self.upper_slider)

        # Plot button for the graph group
        self.graph_plot_btn = QPushButton("Plot")
        self.graph_plot_btn.clicked.connect(self.plot_function)

        # Matplotlib Figure and Canvas
        self.figure = Figure(facecolor="#3e3e3e")
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.setup_plot_aesthetics()

        graph_layout.addWidget(self.graph_expr)
        graph_layout.addLayout(bound_layout)
        graph_layout.addWidget(self.graph_plot_btn)
        graph_layout.addWidget(self.canvas)
        graph_group.setLayout(graph_layout)

        # ---------------- Main Layout ----------------
        main_layout = QVBoxLayout()
        splitter = QSplitter(Qt.Orientation.Vertical)
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.addWidget(calc_group)
        container.setLayout(container_layout)
        splitter.addWidget(container)
        splitter.addWidget(graph_group)
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        self.resize(800, 900)

    def setup_plot_aesthetics(self):
        self.ax.clear()
        self.ax.set_facecolor("#2e2e2e")
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_color('white')
        self.figure.tight_layout()

    # ---------------- Calculator Methods ----------------

    def on_calc_button(self, text):
        current = self.calc_input.text()
        if text == "C":
            self.calc_input.clear()
            self.calc_result.clear()
        elif text == "DEL":
            self.calc_input.setText(current[:-1])
        elif text == "=":
            self.calculate_expression()
        elif text in self.button_mapping:
            self.calc_input.setText(current + self.button_mapping[text])
        else:
            self.calc_input.setText(current + text)

    def calculate_expression(self):
        expr = self.calc_input.text()
        self.calc_result.setText("Calculating...")
        self.eval_thread = EvaluationThread(expr, ALLOWED_NAMES)
        self.eval_thread.result_signal.connect(self.display_calc_result)
        self.eval_thread.start()

    def display_calc_result(self, result):
        self.calc_result.setText(str(result))

    def plot_from_calc(self):
        # If the calculator expression contains 'x', use it for graphing.
        expr = self.calc_input.text()
        if "x" in expr:
            self.graph_expr.setText(expr)
            self.plot_function()
        else:
            self.calc_result.setText("No variable 'x' found for plotting.")

    # ---------------- Graph Methods ----------------

    def sync_lower_field(self, value):
        self.lower_field.setText(str(value/10))  # scale slider value
    def sync_upper_field(self, value):
        self.upper_field.setText(str(value/10))
    def sync_lower_slider(self):
        try:
            val = float(self.lower_field.text())
            self.lower_slider.setValue(int(val*10))
        except ValueError:
            pass
    def sync_upper_slider(self):
        try:
            val = float(self.upper_field.text())
            self.upper_slider.setValue(int(val*10))
        except ValueError:
            pass

    def plot_function(self):
        expr = self.graph_expr.text()
        try:
            lower = float(self.lower_field.text())
            upper = float(self.upper_field.text())
        except ValueError:
            self.ax.clear()
            self.ax.text(0.5, 0.5, "Invalid boundaries", horizontalalignment='center',
                         verticalalignment='center', transform=self.ax.transAxes, color='white')
            self.canvas.draw()
            return
        self.ax.clear()
        self.ax.text(0.5, 0.5, "Calculating...", horizontalalignment='center',
                     verticalalignment='center', transform=self.ax.transAxes, color='white')
        self.canvas.draw()
        self.graph_thread = GraphThread(expr, lower, upper)
        self.graph_thread.plot_signal.connect(self.update_graph)
        self.graph_thread.error_signal.connect(self.display_graph_error)
        self.graph_thread.start()

    def update_graph(self, x, y):
        self.ax.clear()
        # Create a colorful gradient line using a colormap
        segments = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([segments[:-1], segments[1:]], axis=1)
        norm = plt.Normalize(x.min(), x.max())
        cmap = plt.get_cmap("plasma")
        lc = LineCollection(segments, cmap=cmap, norm=norm)
        lc.set_array(x)
        lc.set_linewidth(3)
        line = self.ax.add_collection(lc)
        self.ax.set_xlim(x.min(), x.max())
        self.ax.set_ylim(np.nanmin(y), np.nanmax(y))
        self.ax.set_facecolor("#2e2e2e")
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_color('white')
        # Optionally, add a gradient fill under the curve
        self.ax.fill_between(x, y, color="none", hatch="///", edgecolor="cyan", alpha=0.2)
        self.canvas.draw()

    def display_graph_error(self, message):
        self.ax.clear()
        self.ax.text(0.5, 0.5, message, horizontalalignment='center',
                     verticalalignment='center', transform=self.ax.transAxes, color='white')
        self.canvas.draw()

    # ---------------- State Persistence ----------------

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    state = json.load(f)
                self.calc_input.setText(state.get("calc_expression", ""))
                self.graph_expr.setText(state.get("graph_expression", ""))
                self.lower_field.setText(str(state.get("graph_lower", "-10")))
                self.upper_field.setText(str(state.get("graph_upper", "10")))
                # Sync sliders with field values
                self.sync_lower_slider()
                self.sync_upper_slider()
            except Exception:
                pass

    def save_state(self):
        state = {}
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    state = json.load(f)
            except Exception:
                state = {}
        state["calc_expression"] = self.calc_input.text()
        state["graph_expression"] = self.graph_expr.text()
        try:
            state["graph_lower"] = float(self.lower_field.text())
        except Exception:
            state["graph_lower"] = -10
        try:
            state["graph_upper"] = float(self.upper_field.text())
        except Exception:
            state["graph_upper"] = 10
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(state, f)
        except Exception:
            pass

    def closeEvent(self, event):
        self.save_state()
        event.accept()

# ---------------- Main Application ----------------

def main():
    app = QApplication(sys.argv)
    QLocale.setDefault(QLocale(QLocale.Language.English))
    calc = IntegratedCalculator()
    calc.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
