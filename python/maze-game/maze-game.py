from cmath import isinf
from typing import Union
import json
from math import floor
import os
import sys
from time import time
import pygame

# Type aliases
FloatOrInt = Union[int, float]
RectType = tuple[FloatOrInt, FloatOrInt, FloatOrInt, FloatOrInt]


# Constants
configuration_file = "game-data.json"  # Game data
keymap = {
    # Mapping of keys to actions in game
    "start": [pygame.K_SPACE, pygame.K_r, pygame.K_RETURN, pygame.K_KP_ENTER],
    "up": [pygame.K_UP, pygame.K_w, pygame.K_KP_8],
    "down": [pygame.K_DOWN, pygame.K_s, pygame.K_KP_2],
    "left": [pygame.K_LEFT, pygame.K_a, pygame.K_KP_4],
    "right": [pygame.K_RIGHT, pygame.K_d, pygame.K_KP_6],
    # "menu": [pygame.K_HOME, pygame.K_ESCAPE, pygame.K_m]
}

# Load game settings from config file
game = None
levels = []

def load_game_data():
    global game
    global levels
    with open(os.path.join(sys.path[0], configuration_file)) as f:
        game = json.load(f)
        levels = game["levels"]

load_game_data()

# Variables
# Player positioning
player_x_velocity = 0
player_y_velocity = 0
player_x_position = 0
player_y_position = 0
old_player_x_position = 0
old_player_y_position = 0

# Player bonuses
player_speed_multiplier = 1

# Game logic
game_is_running = True
previous_time = time()
current_level = None
current_level_number = 0
game_won = False
win_message_rendered = False

# Fonts - these can't be inilaized until pygame is loaded
title_font = None
gui_font = None

# Used for things that change colour
loop_ticker = 0.0

# Track parts of the screen that have changed
dirty_rectangles = []

# Game timer
game_running_time = 0

# FPS meter
clock = None

# Functions


def hsv_to_rgb(h, s, v):
    # Credit for this awsome function goes to @Tcll on stack overflow.
    #  Source: https://stackoverflow.com/a/26856771

    if s == 0.0:
        v *= 255
        return (v, v, v)
    i = int(h*6.)  # XXX assume int() truncates!
    f = (h*6.)-i
    p, q, t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))
                                       ), int(255*(v*(1.-s*(1.-f))))
    v *= 255
    i %= 6
    if i == 0:
        return (v, t, p)
    if i == 1:
        return (q, v, p)
    if i == 2:
        return (p, v, t)
    if i == 3:
        return (p, q, v)
    if i == 4:
        return (t, p, v)
    if i == 5:
        return (v, p, q)


def simple_do_two_rects_collide(rect1: RectType, rect2: RectType) -> bool:
    # Returns True if there's a collision, False if not

    # Rect: (x, y, width, height)

    rect1_right = rect1[0] + rect1[2] 
    rect1_bottom = rect1[1] + rect1[3]
    rect2_right = rect2[0] + rect2[2]
    rect2_bottom = rect2[1] + rect2[3]

    # Right side of rect 1 is to the right of rect 2's left side
    left_does_collide = rect1_right > rect2[0]
    # Left side of rect 1 is to the left of rect 2's right side
    right_does_collide = rect1[0] < rect2_right
    # Bottom side of rect 1 is bellow rect 2's top side
    top_does_collide = rect1_bottom > rect2[1]
    # Top side of rect 1 is above rect 2's bottom side
    bottom_does_collide = rect1[1] < rect2_bottom

    if left_does_collide and right_does_collide and top_does_collide and bottom_does_collide:
        print(rect1, rect2, True)
        return True
    print(rect1, rect2, False)
    return False


def draw_timer(window: pygame.Surface, big: bool = False):
    global dirty_rectangles

    rounded_time = round(game_running_time)
    message_to_render = f"Timer: {rounded_time}"

    font = gui_font
    if big:
        font = title_font

    text_position = pygame.Rect(
        window.get_width() - 70, 0, 70, game["gui_height"])

    # Render text
    text = font.render(message_to_render, True, game["gui_text_colour"])

    # Draw black background for text
    pygame.draw.rect(window, game["background_colour"], text_position)

    # Paste text onto screen
    window.blit(text, text_position)

    # Re-draw screen
    dirty_rectangles.append(text_position)


def draw_fps(window: pygame.Surface):
    fps = clock.get_fps()
    if not isinf(fps):
        fps = round(fps)
    message_to_render = f"FPS: {fps}"

    text_position = pygame.Rect(
        window.get_width() - 130, 0, 50, game["gui_height"])

    # Render text
    text = gui_font.render(message_to_render, True, game["gui_text_colour"])

    # Draw black background for text
    pygame.draw.rect(window, game["background_colour"], text_position)

    # Paste text onto screen
    window.blit(text, text_position)

    # Re-draw screen
    dirty_rectangles.append(text_position)


def draw_multiplier():

    pass


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
    for object in current_level["objects"]:
        if object["type"] == "level-end":
            # Draw changing-colour square with border to make it stand out
            colour = hsv_to_rgb(loop_ticker, 0.5, 0.9)
            border_colour = hsv_to_rgb(loop_ticker, 0.2, 1)
            # Draw border
            pygame.draw.rect(
                window,  border_colour, (object["x"], object["y"] + game["gui_height"], object["width"], object["height"]))

            # Draw contents
            pygame.draw.rect(
                window, colour, (object["x"] + 3, object["y"] + game["gui_height"] + 3, object["width"] - 6, object["height"] - 6))
            dirty_rectangles.append(
                (object["x"], object["y"] + game["gui_height"], object["width"], object["height"]))

        if object["type"] == "collectable":
            # Draw changing-colour square with border to make it stand out
            colour = current_level["wall_colour"]
            if object["variant"] == "speed":
                colour = game["speed_powerup_colour"]

            border_colour = hsv_to_rgb(loop_ticker, 0.2, 1)
            # Draw border
            pygame.draw.rect(
                window,  border_colour, (object["x"], object["y"] + game["gui_height"], object["width"], object["height"]))

            # Draw hole
            pygame.draw.rect(
                window, game["background_colour"], (object["x"] + 3, object["y"] + game["gui_height"] + 3, object["width"] - 6, object["height"] - 6))

            # Draw contents
            pygame.draw.rect(
                window, colour, (object["x"] + 8, object["y"] + game["gui_height"] + 8, object["width"] - 16, object["height"] - 16))

            dirty_rectangles.append(
                (object["x"], object["y"] + game["gui_height"], object["width"], object["height"]))


def draw_level(window: pygame.Surface):
    # Called at level start
    global dirty_rectangles

    # Add a black background
    window.fill(game["background_colour"])

    # Draw objects
    for object in current_level["objects"]:
        colour = current_level["wall_colour"]
        pygame.draw.rect(window, colour,
                         (object["x"], object["y"] + game["gui_height"], object["width"], object["height"]))

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
            (game["width"], game["height"] + game["gui_height"]))

        # Update window title
        pygame.display.set_caption("You win!" + " - " + game["title"])
    else:
        # Update current level variable
        current_level = levels[level_number]
        flags = 0
        if current_level["window_resizable"]:
            flags |= pygame.RESIZABLE  # Binary OR asignment operator

        # Update window size
        pygame.display.set_mode(
            (current_level["width"], current_level["height"] + game["gui_height"]), flags=flags)

        # Update window title
        pygame.display.set_caption(
            current_level["name"] + " - " + game["title"])

        # Reset player position
        # Need to do this before drawing the level otherwise a hole might appear in one of the walls
        # "player_start_position": [0, 0],
        if "player_start_position_x" in current_level and "player_start_position_y" in current_level:
            reset_player_position(
                window, current_level["player_start_position_x"], current_level["player_start_position_y"])
        else:
            reset_player_position(window, None, None)

        # Draw level
        draw_level(window)


def on_object_hit(window: pygame.Surface, object) -> bool:
    # Handle collisions
    global current_level_number
    global current_level
    global player_speed_multiplier

    # walls just colide
    if object["type"] == "wall":
        return True

    if object["type"] == "ghost-wall":
        return False

    # Level-end objects don't colide and load the next level
    if object["type"] == "level-end":
        current_level_number += 1
        load_level(window, current_level_number)
        return False

    # Collectabe objects don't collide and add bonuses
    if object["type"] == "collectable":
        if object["variant"] == "speed":
            # Add speed bonus
            player_speed_multiplier += object["bonus"]
        # Destory collectible now that it's been used

        # Remove object from list of objects
        # Wrap this in try/catch because when the player moves into a pickup diagonally the collision detection will call this twice
        try:
            current_level["objects"].remove(object)
        except Exception as exception:
            print(
                f"The weird thing where it ocasionally crashes when you collect a pickup happened: {exception}")

        # Redraw area where box was
        pygame.draw.rect(window, game["background_colour"], (
            object["x"], object["y"] + game["gui_height"], object["width"], object["height"]))
        dirty_rectangles.append(
            (object["x"], object["y"] + game["gui_height"], object["width"], object["height"]))

        return False

    # Return false by default
    return False


# Start pygame
pygame.init()

# Load fonts
title_font = pygame.font.SysFont(None, 32, True)
gui_font = pygame.font.SysFont(None, 18)

# Load clock for fps meter
clock = pygame.time.Clock()

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

    # Setup #

    # Tick pygame clock
    # Capping the fps actually makes the game feel way smoother for some reason
    # without the cap it's 5000-1000 fps
    clock.tick(game["fps_cap"])

    # Calculate delta time for animation calculations
    current_time = time()
    delta_time = current_time - previous_time
    previous_time = current_time

    # Utility for drawing changing colour things
    loop_ticker += 0.1 * delta_time
    if (loop_ticker > 255):
        loop_ticker = 0

    keys = pygame.key.get_pressed()

    # If game is won or lost
    if game_won:

        # Render win or lose screen
        if not win_message_rendered:
            win_message_rendered = True

            message = "You win!"
            colour = game["win_text_colour"]  # Gold

            subititle_message = "Press space to play again."

            time_message = f"Your time was {round(game_running_time, 2)} seconds."

            subititle_text_offset = 30
            time_text_offset = 10

            # Draw black background
            window.fill(game["background_colour"])

            # Draw main text in center of window
            main_text = title_font.render(message, True, colour)
            window.blit(main_text, ((window.get_width() // 2) - (main_text.get_width() // 2),
                        (window.get_height() // 2) - (main_text.get_height() // 2)))

            # Draw subtitle
            subititle_text = gui_font.render(
                subititle_message, True, game["gui_text_colour"])
            window.blit(subititle_text, ((window.get_width() // 2) - (subititle_text.get_width() // 2),
                        (window.get_height() // 2) - (subititle_text.get_height() // 2) + main_text.get_height() + subititle_text_offset))

            # Draw time
            time_text = gui_font.render(
                time_message, True, game["gui_text_colour"])
            window.blit(time_text, ((window.get_width() // 2) - (time_text.get_width() // 2),
                        (window.get_height() // 2) - (time_text.get_height() // 2) + main_text.get_height() + time_text_offset))

            # Re-draw screen
            dirty_rectangles.append(
                (0, 0, window.get_width(), window.get_height()))

        # Handle restarts
        # Check if any of the restart keys are pressed
        if any(keys[key] for key in keymap["start"]):
            # Reset variables
            game_won = False
            win_message_rendered = False
            game_running_time = 0
            player_speed_multiplier = 1

            # Relaod game data since some of it gets modified
            load_game_data()

            # Load first level again
            current_level_number = 0
            load_level(window, current_level_number)

    # Gameplay
    else:

        # Timer
        game_running_time += delta_time
        draw_timer(window)

        # FPS meter
        draw_fps(window)

        # Player movement #

        # Movement left
        # Check if any of the left keys are pressed
        if any(keys[key] for key in keymap["left"]):
            player_x_velocity -= game["player_walk_speed"] * \
                delta_time * player_speed_multiplier

        # Movement right
        # Check if any of the right keys are pressed
        if any(keys[key] for key in keymap["right"]):
            player_x_velocity += game["player_walk_speed"] * \
                delta_time * player_speed_multiplier

        # Movement up
        # Check if any of the up keys are pressed
        if any(keys[key] for key in keymap["up"]):
            player_y_velocity -= game["player_walk_speed"] * \
                delta_time * player_speed_multiplier

        # Movement down
        # Check if any of the down keys are pressed
        if any(keys[key] for key in keymap["down"]):
            player_y_velocity += game["player_walk_speed"] * \
                delta_time * player_speed_multiplier

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
        if abs(player_x_velocity) > game["player_max_speed"] * player_speed_multiplier:
            if player_x_velocity > 0:
                player_x_velocity = game["player_max_speed"] * \
                    player_speed_multiplier
            elif player_x_velocity < 0:
                player_x_velocity = game["player_max_speed"] * \
                    player_speed_multiplier * -1

        if abs(player_y_velocity) > game["player_max_speed"] * player_speed_multiplier:
            if player_y_velocity > 0:
                player_y_velocity = game["player_max_speed"] * \
                    player_speed_multiplier
            elif player_y_velocity < 0:
                player_y_velocity = game["player_max_speed"] * \
                    player_speed_multiplier * -1

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
        if player_y_position < 0 + game["gui_height"]:
            player_y_position = 0 + game["gui_height"]
            player_y_velocity = 0

        # Collision with level objects
        # Why aren't I using pygame's Rect classes and built in clossions detection?
        # I tried. I tried so hard. But nothing worked when using pygame Rects.
        # Also their collision detection didn't tell my what side the collision
        # was on so I would have had to create fake 1-pixel-wide rectandles for each side
        # and test all of them. This just works.
        # [:] creates a copy of the list so that modifiying it doesn't cause issues.
        for object in current_level["objects"][:]:

            # Useful for collision detection
            object_rect = (object["x"], object["y"], object["width"], object["height"])

            # Y collisions
            # If the player could be coliding with the object on the X axis...
            if player_x_position + game["player_width"] > object["x"] and player_x_position < object["x"] + object["width"]:

                # If the player is moving down...
                if player_y_velocity > 0:

                    # And they're inside the object...
                    if player_y_position + game["player_height"] > object["y"] + game["gui_height"] and player_y_position + game["player_height"] < object["y"] + game["gui_height"] + object["height"]:

                        # Check if hitting the object should stop player movement, and do any extra logic
                        stops_movment = on_object_hit(window, object)
                        if stops_movment:

                            reset_player_y_position = old_player_y_position

                            # Check if resetting the y position would extract the player from the object
                            if not simple_do_two_rects_collide(
                                (player_x_position, reset_player_y_position,
                                 game["player_width"], game["player_height"]),
                                object_rect
                            ):
                                print("moving down, restting Y would extract", player_y_position, reset_player_y_position)
                                # Reset their position to their position on the previous tick (when they wern't collising) & cancel their velocity
                                player_y_position = reset_player_y_position
                                player_y_velocity = 0

                # If the player is moving up...
                elif player_y_velocity < 0:

                    # And they're inside the object...
                    if player_y_position < object["y"] + object["height"] + game["gui_height"] and player_y_position > object["y"] + game["gui_height"]:

                        # Check if hitting the object should stop player movement, and do any extra logic
                        stops_movment = on_object_hit(window, object)
                        if stops_movment:

                            reset_player_y_position = old_player_y_position

                            # Check if resetting the y position would extract the player from the object
                            if not simple_do_two_rects_collide(
                                (player_x_position, reset_player_y_position,
                                 game["player_width"], game["player_height"]),
                                object_rect
                            ):
                                print("moving up, restting Y would extract", player_y_position, reset_player_y_position)
                                # Reset their position to their position on the previous tick (when they wern't collising) & cancel their velocity
                                player_y_position = reset_player_y_position
                                player_y_velocity = 00

            # X collisions
            # If the player could be coliding with the object on the Y axis...
            if player_y_position + game["player_height"] > object["y"] + game["gui_height"] and player_y_position < object["y"] + object["height"] + game["gui_height"]:

                # If the player is moving right...
                if player_x_velocity > 0:

                    # And they're inside the object...
                    if player_x_position + game["player_width"] > object["x"] and player_x_position + game["player_width"] < object["x"] + object["width"]:

                        # Check if hitting the object should stop player movement, and do any extra logic
                        stops_movment = on_object_hit(window, object)
                        if stops_movment:

                            reset_player_x_position = old_player_x_position

                            # Check if resetting the X position would extract the player from the object
                            if not simple_do_two_rects_collide(
                                (reset_player_x_position, player_y_position,
                                 game["player_width"], game["player_height"]),
                                object_rect
                            ):
                                print("moving right, restting X would extract", player_x_position, reset_player_x_position)
                                # Reset their position to their position on the previous tick (when they wern't collising) & cancel their velocity
                                player_x_position = reset_player_x_position
                                player_x_velocity = 0

                # If the player is moving left...
                elif player_x_velocity < 0:

                    # And they're inside the object...
                    if player_x_position < object["x"] + object["width"] and player_x_position > object["x"]:

                        # Check if hitting the object should stop player movement, and do any extra logic
                        stops_movment = on_object_hit(window, object)
                        if stops_movment:

                            reset_player_x_position = old_player_x_position

                            # Check if resetting the X position would extract the player from the object
                            if not simple_do_two_rects_collide(
                                (reset_player_x_position, player_y_position,
                                 game["player_width"], game["player_height"]),
                                object_rect
                            ):
                                print("moving left, restting X would extract", player_x_position, reset_player_x_position)
                                # Reset their position to their position on the previous tick (when they wern't collising) & cancel their velocity
                                player_x_position = reset_player_x_position
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
