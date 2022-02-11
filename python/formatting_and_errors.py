
#####################
# String formatting #
#####################


third = 1/3
two_thirds = 2/3

print(third)
print(f"{third:g}")
print(f"{two_thirds:g}")

print(f"{third:.3f}")
print(f"{two_thirds:.3f}")


dolars = 5

print(f"${dolars}.00")

# Use the named argument
# 'end' to stop print() from
# adding newline ('\n')
# characters automaticaly.
print("$", end="")
print(dolars, end="")
print(".00")

##################
# Error handling #
##################

uni = input("Nearest university name: ")
bike_amount = int(input("How many bikes? "))

user_input = 0
try:
    user_input = int(input("What is your lucky number? "))
except ValueError:
    print("Not a valid numeric integer.")

print(f"Choice is {user_input}")

print("Please press 1 to access your Library and 2 to view the special offers")
choice = None
while choice == None:
    try:
        inputted_value = int(input())
        if inputted_value == 1 or inputted_value == 2:
            choice = inputted_value
        else:
            print("1 or 2")
    except ValueError:
        print("Need a number")
print(f"You pressed {choice}")
