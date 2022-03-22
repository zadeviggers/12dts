from typing import Union
import json
from math import floor
import os
import sys
from time import time
import pygame
import colorsys

# Constant
configuration_file = "game-data.json"

# Load game settings from config file
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
old_player_x_position = 0
old_player_y_position = 0
game_is_running = True
previous_time = time()
current_level = None
current_level_number = 0
game_won = False
game_lost = False
lose_win_message_rendered = False
win_lose_font = None
# Used for things that change colour
loop_ticker = 0.0
# Track parts of the screen that have changed
dirty_rectangles = []


# Functions

# Credit for this awsome function goes to @cory-kramer on stack overflow.
#  Source: https://stackoverflow.com/a/24852375
def hsv_to_rgb(h, s, v):
    return tuple(abs(round((i * 255))) for i in colorsys.hsv_to_rgb(h, s, v))


def draw_player(window: pygame.Surface):
    global dirty_rectangles

    # Clear out where the player was
    pygame.draw.rect(window, game["background_colour"],
                     (old_player_x_position, old_player_y_position, game["player_width"], game["player_height"]))
    dirty_rectangles.append(
        (floor(old_player_x_position), floor(old_player_y_position), game["player_width"] + 1, game["player_height"] + 1))

    # Re-draw the player in it's new position
    pygame.draw.rect(window, game["player_colour"],
                     (player_x_position, player_y_position, game["player_width"], game["player_height"]))
    dirty_rectangles.append(
        (floor(player_x_position), floor(player_y_position), game["player_width"] + 1, game["player_height"] + 1))


def draw_level_effect_objects(window: pygame.Surface, loop_ticker: int):
    # Called every tick
    global dirty_rectangles
    for object in current_level["layout"]["objects"]:
        if object["type"] == "level-end":
            # Draw changing-colour square with border to make it stand out
            colour = hsv_to_rgb(loop_ticker, 0.5, 0.9)
            border_colour = hsv_to_rgb(loop_ticker, 0.2, 1)
            pygame.draw.rect(
                window,  border_colour, (object["x"], object["y"], object["width"], object["height"]))
            pygame.draw.rect(
                window, colour, (object["x"]+3, object["y"]+3, object["width"] - 6, object["height"] - 6))
            dirty_rectangles.append(
                (object["x"], object["y"], object["width"], object["height"]))


def draw_level(window: pygame.Surface):
    # Called at level start
    global dirty_rectangles

    # Add a black background
    window.fill(game["background_colour"])

    # Draw objects
    for object in current_level["layout"]["objects"]:
        colour = current_level["layout"]["wall_colour"]
        pygame.draw.rect(window, colour,
                         (object["x"], object["y"], object["width"], object["height"]))

    dirty_rectangles.append(
        (0, 0, window.get_width(), window.get_height()))


def draw_everything(window: pygame.Surface):
    draw_player(window)
    draw_level(window)


def reset_player_position(window: pygame.Surface, x_position: Union[int, None], y_position: Union[int, None]):
    global game
    global player_x_position
    global player_y_position

    # Put the player in the bottom center by defualt
    if x_position is not None:
        player_x_position = x_position
    else:
        player_x_position = (window.get_width()//2)-(game["player_width"]//2)

    if y_position is not None:
        player_y_position = y_position
    else:
        player_y_position = window.get_height() - game["player_height"]

    draw_player(window)


def load_level(window: pygame.Surface, level_number: int):
    global current_level
    global game_won
    global dirty_rectangles

    if level_number > len(levels)-1:
        game_won = True

        # Update window size
        pygame.display.set_mode(
            (game["width"], game["height"]))

        # Update window title
        pygame.display.set_caption("You win!" + " - " + game["title"])
    else:
        # Update current level variable
        current_level = levels[level_number]
        flags = 0
        if current_level["window"]["resizable"]:
            flags |= pygame.RESIZABLE

        # Update window size
        pygame.display.set_mode(
            (current_level["window"]["width"], current_level["window"]["height"]), flags=flags)

        # Update window title
        pygame.display.set_caption(
            current_level["name"] + " - " + game["title"])

        # Draw level
        draw_level(window)

        # Reset player position
        # "player_start_position": [0, 0],
        if "player_start_position" in current_level:
            reset_player_position(
                window, current_level["player_start_position"][0], current_level["player_start_position"][1])
        else:
            reset_player_position(window, None, None)


def on_object_hit(window: pygame.Surface, object) -> bool:
    # Handle collisions
    global current_level_number
    global current_level

    # walls just colide
    if object["type"] == "wall":
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


# Game loop
while game_is_running:
    # Loop over events that have happened
    events = pygame.event.get()
    for event in events:
        # When close button pressed, stop game loop
        if event.type == pygame.QUIT:
            game_is_running = False

        # When the user re-sizes the window, re-draw everything
        if event.type == pygame.VIDEORESIZE:
            draw_everything(window)

    # Utility for drawing changing colour things
    loop_ticker += 0.00001
    if (loop_ticker > 255):
        loop_ticker = 0.0

    # If game is won or lost
    if game_lost or game_won:
        if not lose_win_message_rendered:
            lose_win_message_rendered = True

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

            # Re-draw screen
            dirty_rectangles.append(
                (0, 0, window.get_width(), window.get_height()))

    # Gameplay
    else:

        # Setup #

        # Calculate delta time for physics calculations
        current_time = time()
        delta_time = current_time - previous_time
        previous_time = current_time

        keys = pygame.key.get_pressed()

        # Player movement #

        # Movement left
        if keys[pygame.K_LEFT]:
            player_x_velocity -= game["player_walk_speed"] * delta_time
        # Movement right
        if keys[pygame.K_RIGHT]:
            player_x_velocity += game["player_walk_speed"] * delta_time
        # Movement up
        if keys[pygame.K_UP]:
            player_y_velocity -= game["player_walk_speed"] * delta_time
        # Movement down
        if keys[pygame.K_DOWN]:
            player_y_velocity += game["player_walk_speed"] * delta_time

        # Apply drag
        # If moving right
        if player_x_velocity > 0:
            player_x_velocity -= game["drag"] * delta_time

            # If the player was slowed down too much, cancel all their horizontal velocity
            if player_x_velocity < 0:
                player_x_velocity = 0
        # If moving left
        elif player_x_velocity < 0:
            player_x_velocity += game["drag"] * delta_time

            # If the player was slowed down too much, cancel all their horizontal velocity
            if player_x_velocity > 0:
                player_x_velocity = 0

        # If moving up
        if player_y_velocity > 0:
            player_y_velocity -= game["drag"] * delta_time

            # If the player was slowed down too much, cancel all their vertical velocity
            if player_y_velocity < 0:
                player_y_velocity = 0
        # If moving down
        elif player_y_velocity < 0:
            player_y_velocity += game["drag"] * delta_time

            # If the player was slowed down too much, cancel all their vertical velocity
            if player_y_velocity > 0:
                player_y_velocity = 0

        # Clamp velocity
        if abs(player_x_velocity) > game["player_max_speed"]:
            if player_x_velocity > 0:
                player_x_velocity = game["player_max_speed"]
            elif player_x_velocity < 0:
                player_x_velocity = game["player_max_speed"] * -1

        if abs(player_y_velocity) > game["player_max_speed"]:
            if player_y_velocity > 0:
                player_y_velocity = game["player_max_speed"]
            elif player_y_velocity < 0:
                player_y_velocity = game["player_max_speed"] * -1

        # Apply velocity
        player_x_position += player_x_velocity
        player_y_position += player_y_velocity

        # Colision detection #

        # With screen edges

        # Stop player walking off screen
        # Left side
        if player_x_position < 0:
            player_x_position = 0
            player_x_velocity = 0
        # Right side
        if player_x_position > window.get_width() - game["player_width"]:
            player_x_position = window.get_width() - game["player_width"]
            player_x_velocity = 0
        # Bottom
        if player_y_position >= window.get_height()-game["player_height"]:
            player_y_position = window.get_height()-game["player_height"]
            player_y_velocity = 0
        # Top
        if player_y_position < 0:
            player_y_position = 0
            player_y_velocity = 0

        # Collision with level objects
        # Why aren't I using pygame's Rect classes and built in clossions detection?
        # I tried. I tried so hard. But nothing worked when using pygame Rects.
        # Also their collision detection didn't tell my what side the collision
        # was on so I would have had to create fake 1-pizel-wide rectandles for each side
        # and test all of them. This just works.
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
                            # Reset their position to their position on the previous tick (when they wern't collising) & cancel their velocity
                            player_y_position = old_player_y_position
                            player_y_velocity = 0

                # If the player is moving up...
                elif player_y_velocity < 0:

                    # And they're inside the object...
                    if player_y_position < object["y"] + object["height"] and player_y_position > object["y"]:

                        # Check if hitting the object should stop player movement and do any extra logic
                        stops_movment = on_object_hit(window, object)

                        if stops_movment:
                            # Reset their position to their position on the previous tick (when they wern't collising) & cancel their velocity
                            player_y_position = old_player_y_position
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
                            # Reset their position to their position on the previous tick (when they wern't collising) & cancel their velocity
                            player_x_position = old_player_x_position
                            player_x_velocity = 0

                # If the player is moving left...
                elif player_x_velocity < 0:

                    # And they're inside the object...
                    if player_x_position < object["x"] + object["width"] and player_x_position > object["x"]:

                        # Check if hitting the object should stop player movement and do any extra logic
                        stops_movment = on_object_hit(window, object)

                        if stops_movment:
                            # Reset their position to their position on the previous tick (when they wern't collising) & cancel their velocity
                            player_x_position = old_player_x_position
                            player_x_velocity = 0

        # Drawing #

        # Draw animated level objects
        draw_level_effect_objects(window, loop_ticker)

        # Draw the player if they've moved
        if player_x_position - old_player_x_position != 0 or player_y_position-old_player_y_position != 0:
            draw_player(window)

    # Render all changes
    pygame.display.update(dirty_rectangles)

    # Empty list of dirty rectangles
    dirty_rectangles = []

    # Update old player positions
    old_player_x_position = player_x_position
    old_player_y_position = player_y_position


# Stop game
pygame.quit()
