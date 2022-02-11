def ask_for_number(message: str, use_float: bool = False, allowed_numbers: list[int] = None):
    number_caster = int
    number_type = "integer"
    if use_float:
        number_caster = float
        number_type = "floating-point number"

    try:
        inputted_value = number_caster(input(message))
        if allowed_numbers:
            if inputted_value in allowed_numbers:
                return inputted_value
            else:
                print(f"Needs to be {', '.join(allowed_numbers)}")
                return None
        else:
            return inputted_value
    except ValueError:
        print(f"Need a {number_type}")
        return None


def main():
    distance = None
    time = None

    while distance == None or time == None:
        if distance == None:
            distance = ask_for_number(
                "How far have your traveled? (in kilometers) ", use_float=True)
        elif time == None:
            time = ask_for_number(
                "How long did it take you to get there? (in hours) ", use_float=True)

    average_speed = distance / time

    print(f"Your average speed was {average_speed} kilometers per hour.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("User stopped program.")
