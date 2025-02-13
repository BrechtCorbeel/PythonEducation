# 1. Basic for loop
for i in range(5):
    print(i)

# 2. Looping through a list
fruits = ['apple', 'banana', 'cherry']
for fruit in fruits:
    print(fruit)

# 3. Looping through a string
word = "hello"
for char in word:
    print(char)

# 4. Using break in a for loop
for num in range(10):
    if num == 5:
        break
    print(num)

# 5. Using continue in a for loop
for num in range(10):
    if num % 2 == 0:
        continue
    print(num)

# 6. Looping through a dictionary
person = {'name': 'Alice', 'age': 25, 'city': 'New York'}
for key, value in person.items():
    print(key, ":", value)

# 7. Using else with a for loop
for i in range(3):
    print(i)
else:
    print("Loop finished")

# 8. Nested for loops
for i in range(3):
    for j in range(3):
        print(f"i={i}, j={j}")

# 9. Looping through a list with index
colors = ['red', 'green', 'blue']
for index, color in enumerate(colors):
    print(index, color)

# 10. List comprehension with for loop
squares = [x**2 for x in range(5)]
print(squares)

# 11. Iterating over a set
unique_numbers = {1, 2, 3, 4, 5}
for num in unique_numbers:
    print(num)

# 12. Reversing a list with a for loop
numbers = [1, 2, 3, 4, 5]
for num in reversed(numbers):
    print(num)

# 13. Using zip to iterate over multiple lists
names = ['Alice', 'Bob', 'Charlie']
ages = [25, 30, 35]
for name, age in zip(names, ages):
    print(f"{name} is {age} years old")

# 14. Using itertools for infinite iteration
import itertools
counter = itertools.count(10, 2)
for _ in range(5):
    print(next(counter))

# 15. Filtering elements in a for loop
nums = [10, 15, 20, 25, 30]
filtered_nums = [num for num in nums if num > 20]
print(filtered_nums)

# 16. Using try-except inside a for loop
data = ['10', '20', 'invalid', '30']
for item in data:
    try:
        num = int(item)
        print(num)
    except ValueError:
        print(f"Skipping invalid value: {item}")

# 17. Flattening a nested list
nested_list = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat_list = [num for sublist in nested_list for num in sublist]
print(flat_list)

# 18. Using enumerate with a start index
letters = ['a', 'b', 'c']
for index, letter in enumerate(letters, start=1):
    print(index, letter)

# 19. Using a for loop with a custom step
for i in range(0, 20, 3):
    print(i)

# 20. Simulating a do-while loop with a for loop
attempts = 0
for _ in range(1):
    while True:
        print(f"Attempt {attempts}")
        attempts += 1
        if attempts >= 3:
            break
