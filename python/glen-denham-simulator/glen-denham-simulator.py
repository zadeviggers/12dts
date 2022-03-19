import json
import os
import sys
from time import time
import pygame

# Game settings
window_title = "Glen Denham Simulator"
background_colour = (0, 0, 0)
gravity = 2
drag = 2
player_height = 20
player_width = 10
player_colour = (255, 0, 0)
player_jump_height = 0.4
player_walk_speed = 3
player_max_speed = [6, 1]
allowed_jump_amount = 3
levels = []
with open(os.path.join(sys.path[0], "levels.json")) as f:
    levels = json.load(f)


# Variables
player_x_velocity = 0
player_y_velocity = 0
player_x_position = 0
player_y_position = 0
player_jumps_remaining = allowed_jump_amount
game_is_running = True
previous_time = time()
current_level = None


# Functions
def load_level(level_number: int):
    # Update current level variable
    current_level = levels[level_number]

    # Update window size
    pygame.display.set_mode(
        (current_level["window"]["width"], current_level["window"]["height"]))

    # Update window title
    pygame.display.set_caption(window_title + " - " + current_level["name"])

    return current_level


# Start pygame
pygame.init()

# Load the level
current_level = load_level(0)


# Get the window
window = pygame.display.get_surface()

# Start player in center
player_x_position = (window.get_width()//2)-(player_width//2)
player_y_position = (window.get_height()//2)-(player_height//2)

# Game loop
while game_is_running:
    # Setup #

    # Calculate delta time for physics calculations
    current_time = time()
    delta_time = current_time - previous_time
    previous_time = current_time

    # Reset jump counter if player is on ground
    if player_y_position == window.get_height()-player_height:
        player_jumps_remaining = allowed_jump_amount

    # Loop over events that have happened
    for event in pygame.event.get():
        # When close button pressed, stop game loop
        if event.type == pygame.QUIT:
            game_is_running = False
        elif event.type == pygame.KEYDOWN:
            # Jumping should only happen is a key was pressed down, not if it's held.
            if event.key == pygame.K_UP:
                # If the player has jumps left
                if player_jumps_remaining > 0:
                    # Player Y position is from the top of the screen down, so subtracting makes it go up
                    player_y_velocity = player_jump_height * -1

                    # Decrement the remaining jumps counter
                    player_jumps_remaining -= 1

    keys = pygame.key.get_pressed()

    # Player movement #

    # Movement left
    if keys[pygame.K_LEFT]:
        player_x_velocity -= player_walk_speed * delta_time
    # Movement right
    if keys[pygame.K_RIGHT]:
        player_x_velocity += player_walk_speed * delta_time

    # Apply gravity
    # Player Y position is from the top of the screen down, so adding makes it go down
    player_y_velocity += gravity * delta_time

    # Apply drag
    if player_x_velocity > 0:
        player_x_velocity -= drag * delta_time
    elif player_x_velocity < 0:
        player_x_velocity += drag * delta_time

    # Clamp velocity
    if abs(player_x_velocity) > player_max_speed[0]:
        if player_x_velocity > 0:
            player_x_velocity = player_max_speed[0]
        elif player_x_velocity < 0:
            player_x_velocity = player_max_speed[0] * -1

    if abs(player_y_velocity) > player_max_speed[1]:
        if player_y_velocity > 0:
            player_y_velocity = player_max_speed[1]
        elif player_y_velocity < 0:
            player_y_velocity = player_max_speed[1] * -1

    # Apply velocity
    player_x_position += player_x_velocity
    player_y_position += player_y_velocity

    # Colision detection #

    # With screen edges

    # Stop player falling off screen
    if player_y_position >= window.get_height()-player_height:
        player_y_position = window.get_height()-player_height
        player_y_velocity = 0

    # Stop player walking off screen
    if player_x_position < 0:
        player_x_position = 0
        player_x_velocity = 0
    if player_x_position > window.get_width() - player_width:
        player_x_position = window.get_width() - player_width
        player_x_velocity = 0

    # With platforms
    for platform in current_level["layout"]["platforms"]:

        # If the player could be coliding with the platform on the X axis...
        if player_x_position + player_width > platform["x"] and player_x_position < platform["x"] + platform["width"]:

            # If the player is moving down...
            if player_y_velocity > 0:

                # And they're inside the platform...
                if player_y_position + player_height > platform["y"] and player_y_position + player_height < platform["y"] + platform["height"]:

                    # Reset their position to the bottom side of the platform
                    player_y_position = platform["y"] - player_height
                    player_y_velocity = 0

                    # Since the player is standing on something, also reset their remaining jumps
                    player_jumps_remaining = allowed_jump_amount

            # If the player is moving up...
            elif player_y_velocity < 0:

                # And they're inside the platform...
                if player_y_position < platform["y"] + platform["height"] and player_y_position > platform["y"]:

                    # Reset their position to the top side of the platform
                    player_y_position = platform["y"] + platform["height"]
                    player_y_velocity = 0

        # If the player could be coliding with the platform on the Y axis...
        if player_y_position + player_height > platform["y"] and player_y_position < platform["y"] + platform["height"]:

            # If the player is moving right...
            if player_x_velocity > 0:

                # And they're inside the platform...
                if player_x_position + player_width > platform["x"] and player_x_position + player_width < platform["x"] + platform["width"]:

                    # Reset their position to the left side of the platform
                    player_x_position = platform["x"] - player_width
                    player_x_velocity = 0

            # If the player is moving left...
            elif player_x_velocity < 0:

                # And they're inside the platform...
                if player_x_position < platform["x"] + platform["width"] and player_x_position > platform["x"]:

                    # Reset their position to the right side of the platform
                    player_x_position = platform["x"] + platform["width"]
                    player_x_velocity = 0

    # Drawing #

    # Clear window
    window.fill(background_colour)

    # Draw platforms
    for platform in current_level["layout"]["platforms"]:
        pygame.draw.rect(window, current_level["layout"]["platform_colour"],
                         (platform["x"], platform["y"], platform["width"], platform["height"]))

    # Draw the player
    pygame.draw.rect(window, player_colour,
                     (player_x_position, player_y_position, player_width, player_height))

    # Render all changes
    pygame.display.update()


# Stop game
pygame.quit()
