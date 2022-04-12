my_dict = {
    "cool": True,
    "things": [
        1,
        2,
        3
    ]
}
print(my_dict)

my_list = my_dict["things"][:]
print(my_list)

my_list[0] = 6
print(my_dict)
print(my_list)