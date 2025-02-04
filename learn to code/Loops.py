# ==========================
# 1. Repetition: Repeating a Piece of Code
# ==========================
def push_ups(count):
    """Print a repeated instruction for an exercise."""
    for i in range(count):
        print("Do a push-up!")

print("1. Starting exercise:")
push_ups(10)  # Expected output: "Do a push-up!" printed 10 times

# ==========================
# 2. While Loop: As Long as a Condition is True
# ==========================
def keep_running(meters):
    """Keep running until the desired distance is covered."""
    distance = 0
    while distance < meters:
        print(f"You have run {distance} meters.")
        distance += 50  # Step per iteration

    print("You have reached your goal!")

print("2. Running exercise:")
keep_running(500)  # Expected output: Updates every 50m and stops at 500m

# ==========================
# 3. Iteration: Counting Step by Step
# ==========================
def countdown(start):
    """Count down from a given number to 0."""
    while start >= 0:
        print(start)
        start -= 1  # Counting down

print("3. Countdown:")
countdown(5)  # Expected output: 5, 4, 3, 2, 1, 0

# ==========================
# 4. Counter Variable: Keeping Track of a Value
# ==========================
def double_number(n):
    """Double a number until it exceeds 1000."""
    while n < 1000:
        print(f"Number is now: {n}")
        n *= 2  # Doubling

print("4. Doubling:")
double_number(5)  # Expected output: 5, 10, 20, ..., until it exceeds 1000

# ==========================
# 5. Stopping on a Condition (With Input)
# ==========================
def sum_until_stop():
    """Ask the user for numbers and sum them until they enter 'stop'."""
    total = 0
    while True:
        entry = input("Enter a number (or type 'stop' to quit): ")
        if entry.lower() == "stop":
            break  # Stop the loop
        total += int(entry)
    
    print("The total sum is:", total)

# print("5. Sum until stop:")
# sum_until_stop()  # Requires user input

# ==========================
# 6. Continue: Skipping Some Iterations
# ==========================
def only_even_numbers():
    """Print only the even numbers between 1 and 10."""
    n = 0
    while n < 10:
        n += 1
        if n % 2 != 0:
            continue  # Skip odd numbers
        print(n)

print("6. Only even numbers:")
only_even_numbers()  # Expected output: 2, 4, 6, 8, 10

# ==========================
# 7. Stopping When the User Makes a Mistake
# ==========================
import random

def guess_number():
    """Let the user guess a random number between 1 and 10."""
    secret = random.randint(1, 10)
    while True:
        guess = int(input("Guess the number (1-10): "))
        if guess == secret:
            print("Correct guess!")
            break
        else:
            print("Wrong! Try again.")

# print("7. Guess the number:")
# guess_number()  # Requires user input

# ==========================
# 8. Counting in Steps
# ==========================
def count_by_threes():
    """Count up to 30 in steps of 3."""
    n = 0
    while n <= 30:
        print(n)
        n += 3

print("8. Counting in steps:")
count_by_threes()  # Expected output: 0, 3, 6, ..., 30

# ==========================
# 9. Repeating Patterns
# ==========================
def draw_pyramid(height):
    """Print a pyramid of stars with the given height."""
    n = 1
    while n <= height:
        print("*" * n)
        n += 1

print("9. Pyramid:")
draw_pyramid(5)  # Expected output: A pyramid of 5 rows

# ==========================
# 10. Making Random Choices (Heads or Tails)
# ==========================
def heads_or_tails():
    """Let the user play a heads or tails game."""
    choices = ["heads", "tails"]
    score = 0

    while True:
        choice = input("Heads or tails? (or type 'stop' to quit): ").lower()
        if choice == "stop":
            break
        elif choice not in choices:
            print("Invalid choice! Type 'heads' or 'tails'.")
            continue

        result = random.choice(choices)
        if choice == result:
            print("Correct guess!")
            score += 1
        else:
            print("Too bad! It was", result)

    print("Final score:", score)

# print("10. Heads or tails:")
# heads_or_tails()  # Requires user input
