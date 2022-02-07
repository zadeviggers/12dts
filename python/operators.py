def total_three_ints():

    int1 = int(input("Number 1: "))
    int2 = int(input("Number 2: "))
    int3 = int(input("Number 3: "))
    total = int1+int2+int3
    print(f"Total: {total}")


def average_4_ints():

    int1 = int(input("Number 1: "))
    int2 = int(input("Number 2: "))
    int3 = int(input("Number 3: "))
    int4 = int(input("Number 4: "))

    average = (int1+int2+int3+int4)/4

    print(f"Average: {average}")


def price_per_person():
    bill = float(input("Total bill: $"))
    people = int(input("How many people? "))
    _price_per_person = bill / people
    print(f"Price per person: {_price_per_person}")


def find_area_of_rect():
    width = float(input("Width of rect? "))
    height = float(input("Height of rect? "))

    area = width * height
    print(f"Area: {area} units squared")


def volume_of_box():
    width = float(input("Width of box? "))
    height = float(input("Height of box? "))
    depth = float(input("Depth of box? "))

    volume = width * height * depth
    print(f"Volume: {volume} units cubed")
    return volume


def space_remaining():
    print("Box 1")
    volume1 = volume_of_box()
    print("Box 2")
    volume2 = volume_of_box()

    space_remaining = 0
    if volume1 > volume2:
        space_remaining = volume1 - volume2
    elif volume2 > volume1:
        space_remaining = volume2-volume1
    else:
        print("2 different sizes please!")
        return

    print(f"Space remaining: {space_remaining} units")


total_three_ints()
average_4_ints()
price_per_person()
find_area_of_rect()
volume_of_box()
space_remaining()
