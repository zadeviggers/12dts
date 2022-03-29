from cmath import isinf
from glob import glob
from typing import Union
import json
from math import floor
import os
import sys
from time import time
import pygame

# Constants
configuration_file = "game-data.json"
gui_height = 12

# Load game settings from config file
game = None
levels = []
with open(os.path.join(sys.path[0], configuration_file)) as f:
    game = json.load(f)
    levels = game["levels"]


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
game_lost = False
lose_win_message_rendered = False

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

# Credit for this awsome function goes to @Tcll on stack overflow.
#  Source: https://stackoverflow.com/a/26856771
def hsv_to_rgb(h, s, v):
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


def draw_timer(window: pygame.Surface, big: bool = False):
    global dirty_rectangles

    rounded_time = round(game_running_time)
    message_to_render = f"Timer: {rounded_time}"

    font = gui_font
    if big:
        font = title_font

    text_position = pygame.Rect(window.get_width() - 60, 0, 60, gui_height)

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

    text_position = pygame.Rect(window.get_width() - 140, 0, 80, gui_height)

    # Render text
    text = gui_font.render(message_to_render, True, game["gui_text_colour"])

    # Draw black background for text
    pygame.draw.rect(window, game["background_colour"], text_position)

    # Paste text onto screen
    window.blit(text, text_position)
    
     # Re-draw screen
    dirty_rectangles.append(text_position)


    

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
                window,  border_colour, (object["x"], object["y"] + gui_height, object["width"], object["height"]))
            
            # Draw contents
            pygame.draw.rect(
                window, colour, (object["x"] + 3, object["y"] + gui_height + 3, object["width"] - 6, object["height"] - 6))
            dirty_rectangles.append(
                (object["x"], object["y"] + gui_height, object["width"], object["height"]))
      
        if object["type"] == "collectable":
            # Draw changing-colour square with border to make it stand out
            colour = current_level["wall_colour"]
            if object["variant"] == "speed":
                colour = game["speed_powerup_colour"]
            
            border_colour = hsv_to_rgb(loop_ticker, 0.2, 1)
            # Draw border
            pygame.draw.rect(
                window,  border_colour, (object["x"], object["y"] + gui_height, object["width"], object["height"]))
            
            # Draw hole
            pygame.draw.rect(
                window, game["background_colour"], (object["x"] + 3, object["y"] + gui_height + 3, object["width"] - 6, object["height"] - 6))
            

            # Draw contents
            pygame.draw.rect(
                window, colour, (object["x"] + 8, object["y"]  + gui_height + 8, object["width"] - 16, object["height"] - 16))
            
            dirty_rectangles.append(
                (object["x"], object["y"]  + gui_height, object["width"], object["height"]))


def draw_level(window: pygame.Surface):
    # Called at level start
    global dirty_rectangles

    # Add a black background
    window.fill(game["background_colour"])

    # Draw objects
    for object in current_level["objects"]:
        colour = current_level["wall_colour"]
        pygame.draw.rect(window, colour,
                         (object["x"], object["y"] + gui_height, object["width"], object["height"]))

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
            (game["width"], game["height"] + gui_height))

        # Update window title
        pygame.display.set_caption("You win!" + " - " + game["title"])
    else:
        # Update current level variable
        current_level = levels[level_number]
        flags = 0
        if current_level["window_resizable"]:
            flags |= pygame.RESIZABLE # Binary OR asignment operator

        # Update window size
        pygame.display.set_mode(
            (current_level["width"], current_level["height"] + gui_height), flags=flags)
        
        # Update window title
        pygame.display.set_caption(
            current_level["name"] + " - " + game["title"])

        # Draw level
        draw_level(window)

        # Reset player position
        # "player_start_position": [0, 0],
        if "player_start_position_x" in current_level and "player_start_position_y" in current_level:
            reset_player_position(
                window, current_level["player_start_position_x"], current_level["player_start_position_y"])
        else:
            reset_player_position(window, None, None)


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
        current_level["objects"].remove(object)
        
        # Redraw area where box was
        pygame.draw.rect(window, game["background_colour"], (object["x"], object["y"] + gui_height, object["width"], object["height"]))
        dirty_rectangles.append((object["x"], object["y"] + gui_height, object["width"], object["height"]))
        
        return False

    # Return false by default
    return False


# Start pygame
pygame.init()

# Load fonts
title_font = pygame.font.SysFont(None, 24, True)
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
    if game_lost or game_won:
 
        # Render win or lose screen
        if not lose_win_message_rendered:
            lose_win_message_rendered = True

            message = "You win!"
            colour = (212, 175, 55)  # Gold
            if game_lost:
                message = "You lose"
                colour = (255, 0, 0)  # Red
            
            subititle_message = "Press space to play again"

            # Draw black background
            window.fill(game["background_colour"])
            # Draw text in center of window
            main_text = title_font.render(message, True, colour)
            window.blit(main_text, ((window.get_width() // 2) - (main_text.get_width() // 2),
                        (window.get_height() // 2) - (main_text.get_height() // 2)))
            
            subititle_text = gui_font.render(subititle_message, True, game["gui_text_colour"])
            window.blit(subititle_text, ((window.get_width() // 2) - (subititle_text.get_width() // 2),
                        (window.get_height() // 2) - (subititle_text.get_height() // 2) + main_text.get_height() + 5))

            # Re-draw screen
            dirty_rectangles.append(
                (0, 0, window.get_width(), window.get_height()))

        # Handle restarts
        if keys[pygame.K_SPACE]:
            # Reset variables
            game_lost = False
            game_won = False
            lose_win_message_rendered = False
            game_running_time = 0
            player_speed_multiplier = 1

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
        if keys[pygame.K_LEFT]:
            player_x_velocity -= game["player_walk_speed"] * delta_time * player_speed_multiplier
        # Movement right
        if keys[pygame.K_RIGHT]:
            player_x_velocity += game["player_walk_speed"] * delta_time * player_speed_multiplier
        # Movement up
        if keys[pygame.K_UP]:
            player_y_velocity -= game["player_walk_speed"] * delta_time * player_speed_multiplier
        # Movement down
        if keys[pygame.K_DOWN]:
            player_y_velocity += game["player_walk_speed"] * delta_time * player_speed_multiplier

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
                player_x_velocity = game["player_max_speed"] * player_speed_multiplier
            elif player_x_velocity < 0:
                player_x_velocity = game["player_max_speed"] * player_speed_multiplier * -1

        if abs(player_y_velocity) > game["player_max_speed"] * player_speed_multiplier:
            if player_y_velocity > 0:
                player_y_velocity = game["player_max_speed"] * player_speed_multiplier
            elif player_y_velocity < 0:
                player_y_velocity = game["player_max_speed"] * player_speed_multiplier * -1

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
        if player_y_position < 0 + gui_height:
            player_y_position = 0 + gui_height
            player_y_velocity = 0

        # Collision with level objects
        # Why aren't I using pygame's Rect classes and built in clossions detection?
        # I tried. I tried so hard. But nothing worked when using pygame Rects.
        # Also their collision detection didn't tell my what side the collision
        # was on so I would have had to create fake 1-pizel-wide rectandles for each side
        # and test all of them. This just works.
        for object in current_level["objects"]:

            # If the player could be coliding with the object on the X axis...
            if player_x_position + game["player_width"] > object["x"] and player_x_position < object["x"] + object["width"]:

                # If the player is moving down...
                if player_y_velocity > 0:

                    # And they're inside the object...
                    if player_y_position + game["player_height"] > object["y"]  + gui_height and player_y_position + game["player_height"] < object["y"]  + gui_height + object["height"]:

                        # Check if hitting the object should stop player movement and do any extra logic
                        stops_movment = on_object_hit(window, object)

                        if stops_movment:
                            # Reset their position to their position on the previous tick (when they wern't collising) & cancel their velocity
                            player_y_position = old_player_y_position
                            player_y_velocity = 0

                # If the player is moving up...
                elif player_y_velocity < 0:

                    # And they're inside the object...
                    if player_y_position < object["y"] + object["height"] + gui_height and player_y_position > object["y"] + gui_height:

                        # Check if hitting the object should stop player movement and do any extra logic
                        stops_movment = on_object_hit(window, object)

                        if stops_movment:
                            # Reset their position to their position on the previous tick (when they wern't collising) & cancel their velocity
                            player_y_position = old_player_y_position
                            player_y_velocity = 0

            # If the player could be coliding with the object on the Y axis...
            if player_y_position + game["player_height"] > object["y"] + gui_height and player_y_position < object["y"] + object["height"] + gui_height:

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
