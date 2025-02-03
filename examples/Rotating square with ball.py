import sys
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtGui import QPainter, QColor, QTransform
from PyQt5.QtCore import Qt, QTimer, QPointF


class BallInRotatingSquare(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Rotating Square with Bounded Ball")
        self.setGeometry(100, 100, 600, 600)
        self.square_size = 300
        self.ball_radius = 20
        self.rotation_angle = 0
        self.mouse_pos = QPointF(self.width() / 2, self.height() / 2)  # Track the mouse position
        self.ball_pos = QPointF(self.width() / 2, self.height() / 2)   # Actual ball position

        # Timer for rotation animation and recalculations
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_rotation_and_ball)
        self.timer.start(16)  # Roughly 60 FPS

        self.setMouseTracking(True)
        self.central_widget = RotatingSquareWidget(self)
        self.setCentralWidget(self.central_widget)

    def mouseMoveEvent(self, event):
        # Update the tracked mouse position
        self.mouse_pos = QPointF(event.x(), event.y())
        self.recalculate_ball_position()

    def recalculate_ball_position(self):
        """Recalculate the ball position relative to the rotating square."""
        center_x, center_y = self.width() / 2, self.height() / 2
        square_half = self.square_size / 2

        # Convert mouse position into the square's rotated local coordinate system
        local_mouse = self.rotate_point(self.mouse_pos.x(), self.mouse_pos.y(),
                                         center_x, center_y, -self.rotation_angle)

        # Constrain ball to the square's boundaries in local coordinates
        constrained_x = max(-square_half + self.ball_radius,
                            min(local_mouse.x() - center_x, square_half - self.ball_radius))
        constrained_y = max(-square_half + self.ball_radius,
                            min(local_mouse.y() - center_y, square_half - self.ball_radius))

        # Convert back to the global rotated frame
        constrained_global = self.rotate_point(center_x + constrained_x,
                                               center_y + constrained_y,
                                               center_x, center_y,
                                               self.rotation_angle)

        # Update ball position
        self.ball_pos = QPointF(constrained_global.x(), constrained_global.y())

    def update_rotation_and_ball(self):
        """Update the rotation and recalculate the ball's position."""
        self.rotation_angle = (self.rotation_angle + 2) % 360  # Increment rotation angle
        self.recalculate_ball_position()
        self.central_widget.update()

    @staticmethod
    def rotate_point(x, y, cx, cy, angle):
        """Rotate a point (x, y) around a center (cx, cy) by angle degrees."""
        radians = math.radians(angle)
        dx, dy = x - cx, y - cy
        rotated_x = cx + dx * math.cos(radians) - dy * math.sin(radians)
        rotated_y = cy + dx * math.sin(radians) + dy * math.cos(radians)
        return QPointF(rotated_x, rotated_y)


class RotatingSquareWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_rotating_square(painter)
        self.draw_ball(painter)

    def draw_rotating_square(self, painter):
        square_size = self.parent.square_size
        center_x, center_y = self.width() / 2, self.height() / 2

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(60, 60, 60))  # Dark gray square

        # Apply rotation
        transform = QTransform()
        transform.translate(center_x, center_y)
        transform.rotate(self.parent.rotation_angle)
        transform.translate(-center_x, -center_y)
        painter.setTransform(transform)

        # Draw square centered in the window
        painter.drawRect(int(center_x - square_size / 2), int(center_y - square_size / 2),
                         int(square_size), int(square_size))

    def draw_ball(self, painter):
        ball_radius = self.parent.ball_radius
        ball_pos = self.parent.ball_pos

        # Reset transformation to ensure the ball does not rotate
        painter.resetTransform()
        painter.setBrush(QColor(200, 50, 50))  # Red ball
        painter.setPen(Qt.NoPen)

        # Draw the ball
        painter.drawEllipse(int(ball_pos.x() - ball_radius),
                            int(ball_pos.y() - ball_radius),
                            int(ball_radius * 2), int(ball_radius * 2))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BallInRotatingSquare()
    window.show()
    sys.exit(app.exec_())
