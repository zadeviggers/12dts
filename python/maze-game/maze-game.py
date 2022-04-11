from cmath import isinf
from typing import Union
import json
from math import floor
import os
import sys
from time import time
import webbrowser
import pygame

# Type aliases
FloatOrInt = Union[int, float]
RectType = tuple[FloatOrInt, FloatOrInt, FloatOrInt, FloatOrInt]


# Constants
instructions_file =  "ReadMe.html" # Name of instructions HTML file
instructions_path = os.path.realpath(os.path.join(sys.path[0], instructions_file)) # Full path (e.g. C:\users\your-account\..\maze-game\ReadMe.html)
instructions_url = f"file://{instructions_path}" # Web browser URL to instructions file
configuration_file = "game-data.json"  # Game data
keymap = {
    # Mapping of keys to actions in game
    "start": [pygame.K_SPACE, pygame.K_r, pygame.K_RETURN, pygame.K_KP_ENTER],
    "up": [pygame.K_UP, pygame.K_w, pygame.K_KP_8],
    "down": [pygame.K_DOWN, pygame.K_s, pygame.K_KP_2],
    "left": [pygame.K_LEFT, pygame.K_a, pygame.K_KP_4],
    "right": [pygame.K_RIGHT, pygame.K_d, pygame.K_KP_6],
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
player_x_position = 0
player_y_position = 0
old_player_x_position = 0
old_player_y_position = 0
# Player speed
player_x_velocity = 0
player_y_velocity = 0

# Player bonuses
player_speed_multiplier = 1

# Game logic
game_is_running = True
# This is used to calculate the time since the last game tick
previous_time = time()
# This holds all the data for the current level
current_level = None
# The index of the current level in the game's list of levels
current_level_number = 0
game_won = False
win_message_rendered = False

# Fonts - these can't be inilaized until pygame is loaded
# Fonts are used for drawing text at a specific size to the screen
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

# Restart system
ticks_since_restart = 0

# Functions


def hsv_to_rgb(h, s, v):
    # This function converts a hue-saturation-value format colour to a red-green-blue format colour 
    # Credit for this awsome function goes to @Tcll on stack overflow.
    #  Source: https://stackoverflow.com/a/26856771

    if s == 0.0:
        v *= 255
        return (v, v, v)
    i = int(h*6.)  # XXX assume int() truncates!
    f = (h*6.)-i
    p, q, t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f))))
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
    # A function to detect if two rectangles are overlapping    
    # Returns True if two rectangles are colliding

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
        return True
    return False


def draw_timer(window: pygame.Surface, big: bool = False):
    # A function to draw the game timer to the screen
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
    # A function to draw the game FPS (frames per second) to the screen


    fps = clock.get_fps()

    # FPS is infinate on the very first frame which means that it can't be rounded
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


def draw_player(window: pygame.Surface):
    # A function to draw the player to the screen
    global dirty_rectangles

    # Clear out where the player was
    # The redraw function can only use ints, so I floor the actual value and add one to the width to make sure that the whole object is re-drawn
    old_player_drawing_rect = (floor(old_player_x_position), floor(old_player_y_position), game["player_width"] , game["player_height"] )

    pygame.draw.rect(window, game["background_colour"], old_player_drawing_rect)
    dirty_rectangles.append(old_player_drawing_rect)

    # Re-draw the player in it's new position
    # The redraw function can only use ints, so I floor the actual value and add one to the width to make sure that the whole object is re-drawn
    player_drawing_rect = (floor(player_x_position), floor(player_y_position), game["player_width"] , game["player_height"] )
    
    pygame.draw.rect(window, game["player_colour"], player_drawing_rect)
    dirty_rectangles.append(player_drawing_rect)


def draw_level_effect_objects(window: pygame.Surface, loop_ticker: int):
    # A function to draw animted level objects to the screen
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
    # A function to raw the level (walls, powerups, etc)
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


def draw_win_message(window: pygame.Surface):
    # A function that draws the 'You win' message to the screen when the player has won
    global dirty_rectangles

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

def draw_everything(window: pygame.Surface):
    # A function to draw the relevant things to the screen based on wheather the game has been won or not
    if game_won:
        draw_win_message(window)
    else:
        draw_level(window)
        draw_player(window)


def reset_player_position(window: pygame.Surface, x_position: Union[int, None], y_position: Union[int, None]):
    # A function to reset the player's position, either to the level-defined starting position or to the bottom center
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


def load_level(window: pygame.Surface, level_number: int):
    # Loads in a level from the loaded list of levels
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

        # The player doesn't get re-drawn here becuase it gets drawn
        #  by the game loop anyway so it would be pointless,
        #  and doing so also causes some weird rendering issues in
        #  some edge cases.


def on_object_hit(window: pygame.Surface, object) -> bool:
    # A function foir handling player collisions with level objects
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

# Open game instrutions on game start
webbrowser.open(instructions_url)

# Start pygame so that it's functions can be used
pygame.init()

# Load fonts which are used for drawing text to the screen
title_font = pygame.font.SysFont(None, 32, True)
gui_font = pygame.font.SysFont(None, 18)

# Load clock for fps meter
clock = pygame.time.Clock()

# Get the window object, which is used to draw things onto the screen
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
        
        # If the window was maximised or minimized, redraw everything becuase everything gets cleared when this happens for some reason
        if event.type == pygame.ACTIVEEVENT:
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

    # Handle restarts
    # Increment ticks since resatart counter
    ticks_since_restart += 1

    # Check if any of the restart keys are pressed
    # And it's been a few ticks since the game was last restarted
    if any(keys[key] for key in keymap["start"]) and ticks_since_restart > 500:
        # Restart game

        ticks_since_restart = 0

        # Reset gameplay variables
        game_won = False
        win_message_rendered = False
        game_running_time = 0
        player_speed_multiplier = 1
        player_y_velocity = 0
        player_x_velocity = 0
        

        # Reload game data since some of it gets modified
        load_game_data()

        # Load first level again
        current_level_number = 0
        load_level(window, current_level_number)
        draw_player(window)
    
    else:

        # If game is won
        if game_won:
            # Render win screen
            if not win_message_rendered:
                win_message_rendered = True
                draw_win_message(window)

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
                object_rect = (object["x"], object["y"] + game["gui_height"], object["width"], object["height"])

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
                                    # Reset their position to their position on the previous tick (when they wern't collising) & cancel their velocity
                                    player_x_position = reset_player_x_position
                                    player_x_velocity = 0

            # Drawing #

            # Draw animated level objects
            draw_level_effect_objects(window, loop_ticker)

            # Draw the player if they've moved
            if player_x_position - old_player_x_position != 0 or player_y_position-old_player_y_position != 0:
                draw_player(window)

        # Update old player positions
        old_player_x_position = player_x_position
        old_player_y_position = player_y_position

    # Render all changes
    pygame.display.update(dirty_rectangles)

    # Empty list of dirty rectangles
    dirty_rectangles = []


# Stop game
pygame.quit()
