import json
import os
import sys
from time import time
import pygame

# Constant
configuration_file = "game-data.json"

# Load game settings
game = None
levels = []
with open(os.path.join(sys.path[0], configuration_file)) as f:
    game = json.load(f)
    levels = game["levels"]


# Variables
player_x_velocity = 0
player_y_velocity = 0
player_x_position = 0
player_y_position = 0
player_jumps_remaining = game["player_allowed_jump_amount"]
game_is_running = True
previous_time = time()
current_level = None
current_level_number = 0
game_won = False
game_lost = False
win_lose_font = None


# Functions
def reset_player_position(window: pygame.Surface):
    global game
    global player_x_position
    global player_y_position

    # Put the player in the bottom center
    player_x_position = (window.get_width()//2)-(game["player_width"]//2)
    player_y_position = window.get_height() - game["player_height"]


def load_level(window: pygame.Surface, level_number: int):
    global current_level
    global game_won

    if level_number > len(levels)-1:
        game_won = True
    else:
        # Update current level variable
        current_level = levels[level_number]

        # Update window size
        pygame.display.set_mode(
            (current_level["window"]["width"], current_level["window"]["height"]))

        # Update window title
        pygame.display.set_caption(
            game["title"] + " - " + current_level["name"])

        # Reset player position
        reset_player_position(window)


def on_object_hit(window: pygame.Surface, object) -> bool:
    global current_level_number
    global current_level

    # Platforms just colide
    if object["type"] == "platform":
        return True

    # Level-end objects don't colide and load the next level
    if object["type"] == "level-end":
        current_level_number += 1
        load_level(window, current_level_number)
        return False


# Start pygame
pygame.init()

# Load fonts
win_lose_font = pygame.font.SysFont(None, 24)

# Get the window
window = pygame.display.set_mode((game["width"], game["height"]))

# Load the level
load_level(window, current_level_number)


reset_player_position(window)


# Game loop
while game_is_running:

    # Loop over events that have happened
    events = pygame.event.get()
    for event in events:
        # When close button pressed, stop game loop
        if event.type == pygame.QUIT:
            game_is_running = False

    # If game is won or lost
    if game_lost or game_won:
        message = "You win!"
        colour = (212, 175, 55)  # Gold
        if game_lost:
            message = "You lose"
            colour = (255, 0, 0)  # Red

        # Draw black background
        window.fill(game["background_colour"])
        # Draw text in center of window
        text = win_lose_font.render(message, True, colour)
        window.blit(text, ((window.get_width()//2)-(text.get_width()//2),
                    (window.get_height()//2)-(text.get_height()//2)))

    # Gameplay
    else:

        # Setup #

        # Calculate delta time for physics calculations
        current_time = time()
        delta_time = current_time - previous_time
        previous_time = current_time

        # Reset jump counter if player is on ground
        if player_y_position == window.get_height() - game["player_height"]:
            player_jumps_remaining = game["player_allowed_jump_amount"]

        # Loop over events that have happened
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Jumping should only happen is a key was pressed down, not if it's held.
                if event.key == pygame.K_UP:
                    # If the player has jumps left
                    if player_jumps_remaining > 0:
                        # Player Y position is from the top of the screen down, so subtracting makes it go up
                        player_y_velocity = game["player_jump_height"] * -1

                        # Decrement the remaining jumps counter
                        player_jumps_remaining -= 1

        keys = pygame.key.get_pressed()

        # Player movement #

        # Movement left
        if keys[pygame.K_LEFT]:
            player_x_velocity -= game["player_walk_speed"] * delta_time
        # Movement right
        if keys[pygame.K_RIGHT]:
            player_x_velocity += game["player_walk_speed"] * delta_time

        # Apply gravity
        # Player Y position is from the top of the screen down, so adding makes it go down
        player_y_velocity += game["gravity"] * delta_time

        # Apply drag
        if player_x_velocity > 0:
            player_x_velocity -= game["drag"] * delta_time
        elif player_x_velocity < 0:
            player_x_velocity += game["drag"] * delta_time

        # Clamp velocity
        if abs(player_x_velocity) > game["player_max_speed"][0]:
            if player_x_velocity > 0:
                player_x_velocity = game["player_max_speed"][0]
            elif player_x_velocity < 0:
                player_x_velocity = game["player_max_speed"][0] * -1

        if abs(player_y_velocity) > game["player_max_speed"][1]:
            if player_y_velocity > 0:
                player_y_velocity = game["player_max_speed"][1]
            elif player_y_velocity < 0:
                player_y_velocity = game["player_max_speed"][1] * -1

        # Apply velocity
        player_x_position += player_x_velocity
        player_y_position += player_y_velocity

        # Colision detection #

        # With screen edges

        # Stop player falling off screen
        if player_y_position >= window.get_height()-game["player_height"]:
            player_y_position = window.get_height()-game["player_height"]
            player_y_velocity = 0

        # Stop player walking off screen
        if player_x_position < 0:
            player_x_position = 0
            player_x_velocity = 0
        if player_x_position > window.get_width() - game["player_width"]:
            player_x_position = window.get_width() - game["player_width"]
            player_x_velocity = 0

        # With level objects
        for object in current_level["layout"]["objects"]:

            # If the player could be coliding with the object on the X axis...
            if player_x_position + game["player_width"] > object["x"] and player_x_position < object["x"] + object["width"]:

                # If the player is moving down...
                if player_y_velocity > 0:

                    # And they're inside the object...
                    if player_y_position + game["player_height"] > object["y"] and player_y_position + game["player_height"] < object["y"] + object["height"]:

                        # Check if hitting the object should stop player movement and do any extra logic
                        stops_movment = on_object_hit(window, object)

                        if stops_movment:
                            # Reset their position to the bottom side of the object
                            player_y_position = object["y"] - \
                                game["player_height"]
                            player_y_velocity = 0

                            # Since the player is standing on something, also reset their remaining jumps
                            player_jumps_remaining = game["player_allowed_jump_amount"]

                # If the player is moving up...
                elif player_y_velocity < 0:

                    # And they're inside the object...
                    if player_y_position < object["y"] + object["height"] and player_y_position > object["y"]:

                        # Check if hitting the object should stop player movement and do any extra logic
                        stops_movment = on_object_hit(window, object)

                        if stops_movment:
                            # Reset their position to the top side of the object
                            player_y_position = object["y"] + object["height"]
                            player_y_velocity = 0

            # If the player could be coliding with the object on the Y axis...
            if player_y_position + game["player_height"] > object["y"] and player_y_position < object["y"] + object["height"]:

                # If the player is moving right...
                if player_x_velocity > 0:

                    # And they're inside the object...
                    if player_x_position + game["player_width"] > object["x"] and player_x_position + game["player_width"] < object["x"] + object["width"]:

                        # Check if hitting the object should stop player movement and do any extra logic
                        stops_movment = on_object_hit(window, object)

                        if stops_movment:
                            # Reset their position to the left side of the object
                            player_x_position = object["x"] - \
                                game["player_width"]
                            player_x_velocity = 0

                # If the player is moving left...
                elif player_x_velocity < 0:

                    # And they're inside the object...
                    if player_x_position < object["x"] + object["width"] and player_x_position > object["x"]:

                        # Check if hitting the object should stop player movement and do any extra logic
                        stops_movment = on_object_hit(window, object)

                        if stops_movment:
                            # Reset their position to the right side of the object
                            player_x_position = object["x"] + object["width"]
                            player_x_velocity = 0

        # Drawing #

        # Clear window
        window.fill(game["background_colour"])

        # Draw objects
        for object in current_level["layout"]["objects"]:
            colour = current_level["layout"]["platform_colour"]
            if object["type"] == "level-end":
                colour = game["level_end_marker_colour"]
            pygame.draw.rect(window, colour,
                             (object["x"], object["y"], object["width"], object["height"]))

        # Draw the player
        pygame.draw.rect(window, game["player_colour"],
                         (player_x_position, player_y_position, game["player_width"], game["player_height"]))

    # Render all changes
    pygame.display.update()


# Stop game
pygame.quit()
