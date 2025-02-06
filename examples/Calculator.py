import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, 
    QGridLayout, QLabel, QVBoxLayout
)

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def taylor_sin(x, terms=10):
    # sin(x) ~ sum from k=0 to terms-1 of [(-1)^k * x^(2k+1) / (2k+1)!]
    result = 0
    for k in range(terms):
        numerator = ((-1) ** k) * (x ** (2 * k + 1))
        denominator = factorial(2 * k + 1)
        result += numerator / denominator
    return result

def taylor_cos(x, terms=10):
    # cos(x) ~ sum from k=0 to terms-1 of [(-1)^k * x^(2k) / (2k)!]
    result = 0
    for k in range(terms):
        numerator = ((-1) ** k) * (x ** (2 * k))
        denominator = factorial(2 * k)
        result += numerator / denominator
    return result

def taylor_tan(x, terms=10):
    c = taylor_cos(x, terms)
    s = taylor_sin(x, terms)
    if abs(c) < 1e-15:
        return None
    return s / c

def evaluate_expression(expr):
    # Replace sin, cos, tan in the expression
    expr = expr.replace("sin(", "taylor_sin(")
    expr = expr.replace("cos(", "taylor_cos(")
    expr = expr.replace("tan(", "taylor_tan(")
    expr = expr.replace("factorial(", "factorial(")

    try:
        return eval(
            expr,
            {"__builtins__": None}, 
            {
                "taylor_sin": taylor_sin,
                "taylor_cos": taylor_cos,
                "taylor_tan": taylor_tan,
                "factorial": factorial
            }
        )
    except:
        return "Error"

class AdvancedCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Advanced Calculator (PyQt)")
        
        self.input_field = QLineEdit()
        self.result_label = QLabel()
        
        grid = QGridLayout()

        buttons = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2), ("+", 0, 3),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2), ("-", 1, 3),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2), ("*", 2, 3),
            ("0", 3, 0), (".", 3, 1), ("(", 3, 2), (")", 3, 3),
            ("/", 4, 0), ("sin", 4, 1), ("cos", 4, 2), ("tan", 4, 3),
            ("n!", 5, 0), ("C", 5, 1), ("=", 5, 2)
        ]

        for text, row, col in buttons:
            button = QPushButton(text)
            button.clicked.connect(lambda _, t=text: self.on_button_clicked(t))
            grid.addWidget(button, row, col)

        layout = QVBoxLayout()
        layout.addWidget(self.input_field)
        layout.addWidget(self.result_label)
        layout.addLayout(grid)
        self.setLayout(layout)

    def on_button_clicked(self, text):
        if text == "C":
            self.input_field.clear()
            self.result_label.clear()
        elif text == "=":
            expr = self.input_field.text()
            res = evaluate_expression(expr)
            self.result_label.setText(str(res))
        elif text == "n!":
            current = self.input_field.text()
            self.input_field.setText(current + "factorial(")
        elif text in ("sin", "cos", "tan"):
            current = self.input_field.text()
            self.input_field.setText(current + text + "(")
        else:
            current = self.input_field.text()
            self.input_field.setText(current + text)

def main():
    app = QApplication(sys.argv)
    calculator = AdvancedCalculator()
    calculator.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
