import random
from typing import Optional, Union

# Types
number = Union[int, float]
optional_int_or_bool = Optional[number]


# Variables
exit_message = "Okay. Exiting..."
deck_size = 52
suits = {
    "clubs": "♧",
    "spades": "♤",
    "diamonds": "♢",
    "hearts": "♡"

}

# Functions


def get_number_input(type_to_cast_to: number, prompt_text: str, lower_limit: optional_int_or_bool = None, upper_limit: optional_int_or_bool = None):
    """
    A utility function that takes a number type to try and cast to,
    a message to promt the user with,
    and optionaly upper and/or lower limits for the
    number supplied by the user.
    """

    # Variables
    type_help_text = "integer"
    if type_to_cast_to is float:
        type_help_text = "floating point number (a number with a decimal place)"

    range_message = "Please enter a number that is"
    if lower_limit is not None:
        range_message += f" at least {lower_limit}"
        # Add joiner string if an upper limit as also supplied
        if upper_limit is not None:
            range_message += " and"
    if upper_limit is not None:
        range_message += f" at most {upper_limit}"
    range_message += "."

    print(range_message)

    # Loop until the user provides a valid input
    result: Optional[type_to_cast_to] = None
    while result == None:
        # Prompt the user for a value
        print(prompt_text)
        raw_input = input("> ")

        # Show help message if the user asks for help
        if raw_input == "help" or raw_input == "h":
            print(f"""
{"-"*10} Help {"-"*10}
Required number type: numeric {type_help_text}.
{f"Minimum value: {lower_limit}" if lower_limit else ""}
{f"Maximum value: {upper_limit}" if upper_limit else ""}
You can type "help" or "h" to display this message.
You can type "quit", "q", or "exit" to quit the program 
            """)
        # Quit the program if the user requests it
        elif raw_input == "quit" or raw_input == "q" or raw_input == "q":
            print(exit_message)
            exit(0)
        else:
            try:
                # Try to cast the user's input to the type supplied to the function
                parsed_input: number = type_to_cast_to(raw_input)

                """
                This code only runs if the type cast above does not throw an error,
                meaning that parsed_input is a valid number.
                """
                if lower_limit is not None and parsed_input < lower_limit:
                    print(range_message)
                elif upper_limit is not None and parsed_input > upper_limit:
                    print(range_message)
                else:
                    result = parsed_input

            # The user provided an invalid input
            except ValueError:
                print(
                    f"You didn't provide a valid input. Please only input a numeric {type_help_text}.")

    return result


# Main program
def main():
    # Variables
    deck = []
    players = []

    # Generate the deck
    for suit in suits:
        for i in range(deck_size / 4):
            card = {
                "suit": suit,
                "number": i,
                "text": f"{suit} {i}"
            }
            deck.append(card)

    # Shuffle the deck
    random.shuffle(deck)

    # Generate players
    number_of_players = get_number_input(
        int, "How many players? ", lower_limit=2, upper_limit=5)
    for i in range(number_of_players):
        player = {
            "number": i,
            "cards": [],
            "stats": {
                "pairs": 0,
                "tripples": 0,
                "quads": 0
            }
        }
        players.append(player)


# Only run if not being imported
if __name__ == "__main__":
    try:
        main()
    # Handle CTRL+C
    except KeyboardInterrupt:
        print(f"\n{exit_message}")
        exit(0)
