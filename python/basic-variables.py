def calc_gst():
    GST_AMOUNT = 1.5
    item_price = 26
    gst_calculation = item_price * GST_AMOUNT / 10

    print(f"Item price including GST is ${gst_calculation}")


def data_types():
    name = "Mix Master McMaster"
    skux_rating = 9.5
    tracks_dropped = 5
    is_a_boss = True

    print(name)
    print(skux_rating)
    print(tracks_dropped)
    print(is_a_boss)

    print(type(name))
    print(type(skux_rating))
    print(type(tracks_dropped))
    print(type(is_a_boss))


def variables_and_expressions():
    x = 5
    y = 3
    total = x + y
    print(total)


def input_variables():
    uni = input("What is your nearest university? ")
    bike_count = int(input("How many bikes do you own? "))
    air_fare = float(input("Price of flight to Auckland from Dunedin? "))
    print(uni, bike_count, air_fare)


calc_gst()
data_types()
variables_and_expressions()
input_variables()
