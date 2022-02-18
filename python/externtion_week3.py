from email.policy import default
import random
from typing import Optional, Union
from colorama import init, Fore, Back, Style

# Configure modules
init(autoreset=True)

# Types
number = Union[int, float]
optional_int_or_float = Optional[number]


# Variables
exit_message = f"{Fore.MAGENTA}Okay. Exiting...{Fore.RESET}"
default_deck_size = 52
suits = {
    "clubs": f"{Fore.BLACK}♧{Fore.RESET}",
    "spades": f"{Fore.BLACK}♤{Fore.RESET}",
    "diamonds": f"{Fore.RED}♢{Fore.RESET}",
    "hearts": f"{Fore.RED}♡{Fore.RESET}",
    "hearts": f"{Fore.RED}♡{Fore.RESET}"

}
royals = [[11, f"{Fore.YELLOW}Jack{Fore.RESET}"], [
    12, f"{Fore.YELLOW}Queen{Fore.RESET}"], [13, f"{Fore.YELLOW}King{Fore.RESET}"]]
point_giving_card_amounts = [2, 3, 4, 5, 10,
                             50, 100, 500, 1000, 5000, 10000, 100000, 1000000]


# Functions

def get_input(type_to_cast_to: type, prompt_text: str, default: Optional[type] = None, default_text=Optional[str], helper_text: Optional[str] = None, help_command_text: Optional[str] = None, type_help_text: Optional[str] = None):
    """
    A utility function that takes a type to try and cast to,
    a message to promt the user with,
    and optionaly a default value.
    """

    default_message: Optional[str] = None
    if default is not None:
        if default_text is not None:
            default_message = default_text
        else:
            default_message = str(default)

    input_hint = ""
    if helper_text is not None:
        input_hint += f"Please type in {helper_text}"
    if default_message is not None:
        input_hint += f" or just press enter to use the default ({Fore.CYAN}{default}{Fore.RESET})"

    # Loop until the user provides a valid input
    result: Optional[type_to_cast_to] = None

    while result == None:
        # Prompt the user for a value
        print(prompt_text)
        if input_hint != "":
            print(input_hint)
        raw_input = input(f"> {Fore.GREEN}")
        # Stop text colour from spreading where it shouldn't
        print(Fore.RESET, end="")

        # If the users just pressed enter and there's a default value, then use it
        if default is not None and raw_input == "":
            result = default

            print(f"Defaulted to {Fore.CYAN}{default_message}{Fore.RESET}.")

        # Show help message if the user asks for help
        elif help_command_text is not None and (raw_input == "help" or raw_input == "h"):
            print(help_command_text)

        # Quit the program if the user requests it
        elif raw_input == "quit" or raw_input == "q" or raw_input == "q":
            print(exit_message)
            exit(0)

        # It's probably a the correct type
        else:
            try:
                # Try to cast the user's input to the type supplied to the function
                result = type_to_cast_to(raw_input)
            # The user provided an invalid input
            except ValueError:
                if type_help_text is not None:
                    print(
                        f"You didn't provide a valid input. Please only input a {type_help_text}.")
                else:
                    print("Invalid input.")

    return result


def get_number_input(type_to_cast_to: number, prompt_text: str, lower_limit: optional_int_or_float = None, upper_limit: optional_int_or_float = None, default: Optional[str] = None):
    """
    A utility function that wraps the get_input function
    It takes a number type to try and cast to,
    a message to promt the user with,
    and optionaly upper and/or lower limits for the
    number supplied by the user, and a default value.
    """

    # Variables
    type_help_text = "integer"
    if type_to_cast_to is float:
        type_help_text = "floating point number (a number with a decimal place)"

    range_message = "Please enter a number that is"
    if lower_limit is not None:
        range_message += f" at least {Fore.CYAN}{lower_limit}{Fore.RESET}"
        # Add joiner string if an upper limit as also supplied
        if upper_limit is not None:
            range_message += " and"
    if upper_limit is not None:
        range_message += f" at most {Fore.CYAN}{upper_limit}{Fore.RESET}"

    default_message = ""
    if default is not None:
        default_message = f" or just press enter to use the default ({Fore.CYAN}{default}{Fore.RESET})"

    input_help_message = f"{range_message}."

    result: number = 0
    getting_input = True
    while getting_input:
        result = get_input(
            type_to_cast_to, prompt_text, default=default, default_text=default_message, helper_text=input_help_message, help_command_text=f"""
    {"-"*10} Help {"-"*10}
    Required number type: {Fore.BLUE}numeric {type_help_text}{Fore.RESET}.
    {f"Minimum value: {Fore.CYAN}{lower_limit}{Fore.RESET}" if lower_limit else ""}
    {f"Maximum value: {Fore.CYAN}{upper_limit}{Fore.RESET}" if upper_limit else ""}
    You can type "{Fore.GREEN}help{Fore.RESET}" or "{Fore.GREEN}h{Fore.RESET}" to display this message.
    You can type "{Fore.GREEN}quit{Fore.RESET}", "{Fore.GREEN}q{Fore.RESET}", or "{Fore.GREEN}exit{Fore.RESET}" to quit the program
                """, type_help_text=type_help_text)

        if lower_limit is not None and result < lower_limit:
            print(input_help_message)
        elif upper_limit is not None and result > upper_limit:
            print(input_help_message)
        else:
            getting_input = False

    return result


def get_bool_input(prompt: str, default: Optional[bool] = None, default_text: Optional[str] = None):
    helper_text = f"{Fore.GREEN}yes{Fore.RESET} or {Fore.GREEN}no{Fore.RESET}"

    result: Optional[bool] = None
    getting_input = True
    while getting_input:
        inputted_value = get_input(str, prompt, default=default,
                                   default_text=default_text, helper_text=helper_text)
        if inputted_value == True or inputted_value == False:
            result = inputted_value
            getting_input = False
        else:
            inputted_string: str = inputted_value.lower()
            if inputted_string == "true":
                result = True
                getting_input = False
            elif inputted_string == "false":
                result = False
                getting_input = False
            elif inputted_string == "y" or inputted_string == "yes":
                result = True
                getting_input = False
            elif inputted_string == "n" or inputted_string == "no":
                result = False
                getting_input = False
            else:
                print(f"Invalid input. Please type {helper_text}.")

    return result


# Main program

def main():
    # Variables
    deck = []
    players = []

    # Generate players
    print("Generating players...")
    number_of_players = get_number_input(
        int, "How many players? ", lower_limit=2, default=3)
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

    minimum_deck_size = max(52, number_of_players * 2)

    deck_size = get_number_input(
        int, "How many cards in the deck? ", lower_limit=minimum_deck_size, default=minimum_deck_size)

    # Generate the deck
    print("Generating the deck...")
    for suit in suits:
        for i in range(round(deck_size / len(suits))):
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
    print("Shuffling the deck...")
    random.shuffle(deck)

    # Deal cards to players
    print("Dealing cards...")
    next_player_index = random.randrange(0, number_of_players-1)
    for card in deck:
        players[next_player_index]["cards"].append(card)

        if next_player_index == number_of_players-1:
            next_player_index = 0
        else:
            next_player_index += 1

    # Work out points
    print("Calculating points...")
    for player in players:
        # Coutn how many of each card number a player has
        amounts = {}
        for card in player["cards"]:
            if not card["number"] in amounts:
                amounts[card["number"]] = 1
            else:
                amounts[card["number"]] += 1

        # Loop over the amounts and update the player's stats
        for (number, amount) in amounts.items():
            if amount in point_giving_card_amounts:
                players[player["index"]]["stats"]["score"] += amount * 1.1
                if amount == 2:
                    players[player["index"]]["stats"]["pairs"] += 1
                elif amount == 3:
                    players[player["index"]]["stats"]["tripples"] += 1
                elif amount == 4:
                    players[player["index"]]["stats"]["quads"] += 1

    # Determine winner
    print("Determining winner...")
    winner: Optional[dict] = None
    best_score_so_far = -1
    tiers = None
    for player in players:
        # print(
        #     f'Player {player["number"]}\'s hand: {", ".join(card["text"] for card in player["cards"])}')
        if player["stats"]["score"] > best_score_so_far:
            best_score_so_far = player["stats"]["score"]
            winner = player
            tiers = None
        elif player["stats"]["score"] == best_score_so_far:
            if tiers is None:
                tiers = []
            tiers.append(player)
    if tiers is not None:
        print(
            f"""Tie between {', '.join(f'Player {player["number"]} (score: {Fore.CYAN}{player["stats"]["score"]}{Fore.RESET})' for player in tiers)}!""")
    else:
        print(
            f'Player {winner["number"]} wins with a  score of {Fore.CYAN}{winner["stats"]["score"]:.1f}{Fore.RESET}!!')


# Only run if not being imported
if __name__ == "__main__":
    try:
        # Replay loop
        playing = True
        while playing:
            # Run game
            main()

            # Ask the player if they want to play again
            # Keep asking until a valid response is received.
            playing = get_bool_input(
                "Do you want to play again?", default=False, default_text="no")

        print(f"{Fore.MAGENTA}Thanks for playing!{Fore.RESET}")

    # Handle CTRL+C
    except KeyboardInterrupt:
        print(f"\n{exit_message}")
        exit(0)
