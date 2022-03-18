from cmath import rect
from time import time
import pygame

# Game settings
gravity = 3
drag = 2
player_height = 20
player_width = 10
player_colour = (255, 0, 0)
player_jump_height = 0.8
player_walk_speed = 3
player_max_speed = [15, 1600]
allowed_jump_amount = 3

# Variables
player_velocity = [0, 0]
player_position = [0, 0]
jumps_remaining = allowed_jump_amount
game_is_running = True
previous_time = time()
player_is_on_ground = False


# Start pygame
pygame.init()

# Create a 500px by 500px window
window = pygame.display.set_mode((501, 502))

# Give window a title
pygame.display.set_caption("Glen Denham Simulator")

# Start player in center
player_position[0] = (window.get_width()//2)-(player_width//2)
player_position[1] = (window.get_height()//2)-(player_height//2)

# Game loop
while game_is_running:
    # Calculate delta time for physics calculations
    current_time = time()
    delta_time = current_time - previous_time
    previous_time = current_time

    # Keep track of it player is grounded
    if player_position[1] == window.get_height()-player_height:
        player_is_on_ground = True
    else:
        player_is_on_ground = False

    # Reset jump counter if player is on ground
    if player_is_on_ground:
        jumps_remaining = allowed_jump_amount

    # Loop over events that have happened
    for event in pygame.event.get():
        # When close button pressed, stop game loop
        if event.type == pygame.QUIT:
            game_is_running = False
        elif event.type == pygame.KEYDOWN:
            # Jumping should only happen is a key was pressed down, not if it's held.
            if event.key == pygame.K_UP:
                # If the player has jumps left
                if jumps_remaining > 0:
                    # Player Y position is from the top of the screen down, so subtracting makes it go up
                    player_velocity[1] = player_jump_height * -1

                    # Decrement the remaining jumps counter
                    jumps_remaining -= 1

    keys = pygame.key.get_pressed()

    # Movement left
    if keys[pygame.K_LEFT]:
        player_velocity[0] -= player_walk_speed * delta_time
    # Movement right
    if keys[pygame.K_RIGHT]:
        player_velocity[0] += player_walk_speed * delta_time

    # Apply gravity
    # Player Y position is from the top of the screen down, so adding makes it go down
    player_velocity[1] += gravity * delta_time

    # Apply drag
    if player_velocity[0] > 0:
        player_velocity[0] -= drag * delta_time
    elif player_velocity[0] < 0:
        player_velocity[0] += drag * delta_time

    # Clamp velocity
    if abs(player_velocity[0]) > player_max_speed[0]:
        if player_velocity[0] > 0:
            player_velocity[0] = player_max_speed[0]
        elif player_velocity[0] < 0:
            player_velocity[0] = player_max_speed[0] * -1

    if abs(player_velocity[1]) > player_max_speed[1]:
        if player_velocity[1] > 0:
            player_velocity[1] = player_max_speed[1]
        elif player_velocity[1] < 0:
            player_velocity[1] = player_max_speed[1] * -1

    # Apply velocity
    player_position[0] += player_velocity[0]
    player_position[1] += player_velocity[1]

    # Stop player falling off screen
    if player_position[1] >= window.get_height()-player_height:
        player_position[1] = window.get_height()-player_height
        player_velocity[1] = 0

    # Stop player walking off screen
    if player_position[0] < 0:
        player_position[0] = 0
        player_velocity[0] = 0
    if player_position[0] > window.get_width() - player_width:
        player_position[0] = window.get_width() - player_width
        player_velocity[0] = 0

    # Clear window
    window.fill((0, 0, 0))

    # Draw the player
    pygame.draw.rect(window, player_colour,
                     (player_position[0], player_position[1], player_width, player_height))

    # Render all changes
    pygame.display.update()


# Stop game
pygame.quit()
