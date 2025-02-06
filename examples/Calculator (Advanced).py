import sys
import os
import json
import math
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton,
    QGridLayout, QLabel, QVBoxLayout
)

def get_appdata_folder():
    # Determine the application data folder based on OS
    if os.name == 'nt':
        base_dir = os.getenv('APPDATA')
        folder = os.path.join(base_dir, "AdvancedCalculator")
    else:
        # For Linux and others, use a hidden folder in the home directory
        home = os.path.expanduser("~")
        folder = os.path.join(home, ".advanced_calculator")
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

STATE_FILE = os.path.join(get_appdata_folder(), "state.json")

# Allowed names for evaluation (using math module functions and constants)
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
    "asinh": math.asinh,
    "acosh": math.acosh,
    "atanh": math.atanh,
    "log": math.log,      # natural logarithm (ln)
    "log10": math.log10,  # base-10 logarithm
    "exp": math.exp,
    "sqrt": math.sqrt,
    "factorial": math.factorial,
    "pi": math.pi,
    "e": math.e,
    "degrees": math.degrees,
    "radians": math.radians,
    "abs": abs,
    "round": round,
    "pow": pow
}

class EvaluationThread(QThread):
    result_signal = pyqtSignal(object)

    def __init__(self, expression, allowed_names):
        super().__init__()
        self.expression = expression
        self.allowed_names = allowed_names

    def run(self):
        try:
            # Evaluate the expression safely
            result = eval(self.expression, {"__builtins__": None}, self.allowed_names)
        except Exception:
            result = "Error"
        self.result_signal.emit(result)

class AdvancedCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.eval_thread = None
        self.init_ui()
        self.load_state()

    def init_ui(self):
        self.setWindowTitle("Advanced Calculator")
        # Set a dark grey aesthetic for the whole app
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
        """)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter expression...")
        self.result_label = QLabel("")

        grid = QGridLayout()

        # Define the buttons and their positions in the grid.
        # Basic numbers and operators
        buttons = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2), ("/", 0, 3),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2), ("*", 1, 3),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2), ("-", 2, 3),
            ("0", 3, 0), (".", 3, 1), ("(", 3, 2), (")", 3, 3),
            ("+", 4, 0), ("^", 4, 1), ("sqrt", 4, 2), ("exp", 4, 3),
            ("sin", 5, 0), ("cos", 5, 1), ("tan", 5, 2), ("log", 5, 3),
            ("asin", 6, 0), ("acos", 6, 1), ("atan", 6, 2), ("ln", 6, 3),
            ("sinh", 7, 0), ("cosh", 7, 1), ("tanh", 7, 2), ("fact", 7, 3),
            ("pi", 8, 0), ("e", 8, 1), ("deg", 8, 2), ("rad", 8, 3),
            ("C", 9, 0), ("DEL", 9, 1), ("=", 9, 2, 1, 2)  # "=" spans two columns
        ]

        # Add buttons to the grid layout
        for button in buttons:
            # Some buttons might span more than one cell (row, col, rowspan, colspan)
            if len(button) == 3:
                text, row, col = button
                rowspan, colspan = 1, 1
            else:
                text, row, col, rowspan, colspan = button
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, t=text: self.on_button_clicked(t))
            grid.addWidget(btn, row, col, rowspan, colspan)

        layout = QVBoxLayout()
        layout.addWidget(self.input_field)
        layout.addWidget(self.result_label)
        layout.addLayout(grid)
        self.setLayout(layout)

        # Mapping for functions and special operators to be inserted with parentheses.
        self.function_mapping = {
            "sqrt": "sqrt(",
            "exp": "exp(",
            "sin": "sin(",
            "cos": "cos(",
            "tan": "tan(",
            "asin": "asin(",
            "acos": "acos(",
            "atan": "atan(",
            "sinh": "sinh(",
            "cosh": "cosh(",
            "tanh": "tanh(",
            "log": "log10(",
            "ln": "log(",
            "fact": "factorial(",
            "deg": "degrees(",
            "rad": "radians("
        }

    def on_button_clicked(self, text):
        current = self.input_field.text()

        if text == "C":
            self.input_field.clear()
            self.result_label.clear()
        elif text == "DEL":
            self.input_field.setText(current[:-1])
        elif text == "=":
            expr = self.input_field.text()
            # Replace '^' with '**' for power operations.
            expr = expr.replace("^", "**")
            # Start the evaluation thread so the UI remains responsive.
            self.result_label.setText("Calculating...")
            self.eval_thread = EvaluationThread(expr, ALLOWED_NAMES)
            self.eval_thread.result_signal.connect(self.display_result)
            self.eval_thread.start()
        elif text in self.function_mapping:
            # Insert the function call with an opening parenthesis.
            self.input_field.setText(current + self.function_mapping[text])
        else:
            # For all other buttons, simply append the text.
            self.input_field.setText(current + text)

    def display_result(self, result):
        self.result_label.setText(str(result))

    def load_state(self):
        # Load the last entered expression from the state file, if available.
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    state = json.load(f)
                last_expr = state.get("last_expression", "")
                self.input_field.setText(last_expr)
            except Exception:
                pass

    def save_state(self):
        # Save the current expression to the state file.
        state = {
            "last_expression": self.input_field.text()
        }
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(state, f)
        except Exception:
            pass

    def closeEvent(self, event):
        self.save_state()
        event.accept()

def main():
    app = QApplication(sys.argv)
    calc = AdvancedCalculator()
    calc.resize(400, 600)
    calc.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
