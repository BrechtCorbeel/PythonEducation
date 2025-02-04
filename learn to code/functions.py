# ==========================
# 1. Basic Structure of a Function
# ==========================
def multiply(x, y):
    """Multiply two numbers and return the result."""
    return x * y

print("1. Multiplication of 4 and 6:", multiply(4, 6))  # Expected output: 24

# ==========================
# 2. Functions with Parameters and Return Values
# ==========================
import math

def circle_circumference(r):
    """Calculate the circumference of a circle with radius r."""
    return 2 * math.pi * r

print("2. Circumference of a circle with radius 7:", circle_circumference(7))  # Expected output: ~43.98

# ==========================
# 3. Functions without Return (Using Print)
# ==========================
def greet(name):
    """Print a greeting for a person."""
    print(f"3. Hello, {name}! Welcome to the lesson.")

greet("Sophie")

# ==========================
# 4. Using Modules (math and random)
# ==========================
print("4. Cosine of 0 degrees:", math.cos(0))  # Output: 1.0

import random
print("4. Random decimal number between 0 and 1:", random.random())

# ==========================
# 5. Local vs. Global Variables
# ==========================
score = 0  # Global variable

def increase_score():
    """Increase the score by 10."""
    global score
    score += 10

increase_score()
print("5. Score after increase:", score)  # Expected output: 10

# ==========================
# 6. Exercises and Applications
# ==========================
def maximum(a, b):
    """Return the larger of two numbers."""
    return a if a > b else b

print("6. Largest of 8 and 12:", maximum(8, 12))  # Expected output: 12

def is_divisible_by_three(x):
    """Check if a number is divisible by 3."""
    return x % 3 == 0

print("6. Is 9 divisible by 3?", is_divisible_by_three(9))  # Expected output: True

def count_letter(s, letter):
    """Count how many times a specific letter appears in a string."""
    return s.count(letter)

print("6. Number of times 'e' appears in 'teacher':", count_letter("teacher", "e"))  # Expected output: 2

# ==========================
# 7. Pythagoras: Calculating the Hypotenuse
# ==========================
def rectangle_area(length, width):
    """Calculate the area of a rectangle."""
    return length * width

print("7. Area of a rectangle (5x3):", rectangle_area(5, 3))  # Expected output: 15

# ==========================
# 8. Application: Generating a Random Number
# ==========================
def roll_dice():
    """Simulate rolling a six-sided die (1-6)."""
    return random.randint(1, 6)

print("8. Dice roll:", roll_dice())

# ==========================
# 9. Exercise: Calculate Distance Between Two Points
# ==========================
def distance_from_origin(x, y):
    """Calculate the distance from a point (x, y) to the origin (0,0)."""
    return math.sqrt(x**2 + y**2)

print("9. Distance from (5,12) to origin:", distance_from_origin(5, 12))  # Expected output: 13

# ==========================
# 10. Random Number of Jumps Based on Age
# ==========================
def jumps(age):
    """Determine randomly how many jumps someone should make, depending on their age."""
    return random.randint(5, age)

print("10. Jumps for a 25-year-old:", jumps(25))
