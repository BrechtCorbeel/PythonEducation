# ==========================
# 1. Variables: Storing and Overwriting a Value
# ==========================
hobby = "drawing"  # A variable is assigned a value
print("1. Your favorite hobby is:", hobby)

hobby = "soccer"  # The variable is overwritten
print("Your new hobby is:", hobby)

# ==========================
# 2. Values: Using Variables for Calculations
# ==========================
hours_per_day = 3
days_per_week = 5
total_hours = hours_per_day * days_per_week  # Multiplication

print("\n2. You spend", total_hours, "hours per week on your hobby.")

# ==========================
# 3. Combining and Manipulating Variables
# ==========================
name = "Elias"
age = 16

message = name + " is " + str(age) + " years old."
print("\n3.", message)

# ==========================
# 4. Type Differences: Text vs. Numbers
# ==========================
word = "hello"
number = 5

# print(word + number)  # This will cause an error
print("\n4. You cannot add text and numbers together.")

# Solution: Convert the number to a string
print("Solution:", word + str(number))  # Convert number to string

# ==========================
# 5. Type Conversions and Calculations
# ==========================
a = "10"
b = "5"

# print(a + b)  # This concatenates the strings instead of adding them as numbers

a = int(a)  # Convert to integer
b = int(b)  # Convert to integer
print("\n5. Correct sum of 10 and 5:", a + b)

# ==========================
# 6. Manipulating Strings
# ==========================
text = "Python is fun!"
print("\n6. Length of the text:", len(text))
print("The first letter is:", text[0])
print("The last letter is:", text[-1])
print("Uppercase:", text.upper())
print("Lowercase:", text.lower())

# ==========================
# 7. Calculations with Floating-Point Numbers
# ==========================
a = 7.5
b = 2.3

print("\n7. Addition:", a + b)
print("Subtraction:", a - b)
print("Multiplication:", a * b)
print("Division:", a / b)

# ==========================
# 8. Rounding and Modulo Calculations
# ==========================
number = 23.567
print("\n8. Rounded to 2 decimal places:", round(number, 2))

x = 23
y = 7
print("Quotient (integer division):", x // y)  # Integer division
print("Remainder (modulo):", x % y)  # Remainder of division

# ==========================
# 9. Logical Operations
# ==========================
score = 15
print("\n9. Is the score greater than 10?", score > 10)
print("Is the score less than 5?", score < 5)
print("Is the score equal to 15?", score == 15)

# ==========================
# 10. Working with Multiple Variables
# ==========================
num_people = 4
price_per_person = 12.50
total_cost = num_people * price_per_person

print("\n10. The total cost for", num_people, "people is:", total_cost)

