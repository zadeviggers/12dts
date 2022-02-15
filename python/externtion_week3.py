import random
from typing import Optional, Union

# Types
number = Union[int, float]
optional_int_or_float = Optional[number]


# Variables
exit_message = "Okay. Exiting..."
default_deck_size = 52
suits = {
    "clubs": "♧",
    "spades": "♤",
    "diamonds": "♢",
    "hearts": "♡"

}
royals = [[11, "Jack"], [12, "Queen"], [13, "Queen"]]

# Functions


def get_number_input(type_to_cast_to: number, prompt_text: str, lower_limit: optional_int_or_float = None, upper_limit: optional_int_or_float = None, default: Optional[str] = None):
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

    # Generate players
    number_of_players = get_number_input(
        int, "How many players? ", lower_limit=2, upper_limit=420)
    for i in range(number_of_players):
        player = {
            "index": i,
            "number": i + 1,
            "cards": [],
            "stats": {
                "pairs": 0,
                "tripples": 0,
                "quads": 0,
                "score": 0.0
            }
        }
        players.append(player)

    deck_size = max(default_deck_size, number_of_players *
                    random.randrange(14, 19))

    # Generate the deck
    for suit in suits:
        for i in range(round(deck_size / 4)):
            suit_symbol = suits[suit]
            number = i + 1
            number_text = str(number)
            for royal in royals:
                if number % royal[0] == 0:
                    number_text = royal[1]
                    if number != royal[0]:
                        number_text += f" #{royal[0]%number}"

            card = {
                "suit": suit,
                "suit_symbol": suit_symbol,
                "number": number,
                "number_text": number_text,
                "text": f"{suit_symbol} {number_text}"
            }
            deck.append(card)

    # Shuffle the deck
    random.shuffle(deck)
    random.shuffle(deck)

    # Deal cards to players
    next_player_index = random.randrange(0, number_of_players-1)
    for card in deck:
        players[next_player_index]["cards"].append(card)

        if next_player_index == number_of_players-1:
            next_player_index = 0
        else:
            next_player_index += 1

    # Work out points
    for player in players:
        amounts = {}
        for card in player["cards"]:
            if not card["number"] in amounts:
                amounts[card["number"]] = 1
            else:
                amounts[card["number"]] += 1

        for (number, amount) in amounts.items():
            if amount in [2, 3, 4]:
                players[player["index"]]["stats"]["score"] += amount * 1.1
                if amount == 2:
                    players[player["index"]]["stats"]["pairs"] += 1
                elif amount == 3:
                    players[player["index"]]["stats"]["tripples"] += 1
                elif amount == 4:
                    players[player["index"]]["stats"]["quads"] += 1

    # Determin winner
    winner: Optional[dict] = None
    best_score_so_far = -1
    tie = False
    for player in players:
        print(
            f'Player {player["number"]}\'s hand: {", ".join(card["text"] for card in player["cards"])}')
        if player["stats"]["score"] > best_score_so_far:
            best_score_so_far = player["stats"]["score"]
            winner = player
            tie = False
        elif player["stats"]["score"] == best_score_so_far:
            tie = True
    if tie:
        print("Tie!")
    else:
        print(
            f'Player {winner["number"]} wins with a  score of {winner["stats"]["score"]:.1f}!!')


# Only run if not being imported
if __name__ == "__main__":
    try:
        main()
    # Handle CTRL+C
    except KeyboardInterrupt:
        print(f"\n{exit_message}")
        exit(0)
