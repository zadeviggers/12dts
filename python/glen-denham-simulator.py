from cmath import rect
from time import time
import pygame

# Game settings
gravity = 3
drag = 2
player_height = 20
player_width = 10
player_colour = (255, 0, 0)
player_jump_height = 300
player_walk_speed = 3
player_max_speed = [15, 1600]
extra_jumps = 1
jump_cooldown = 0.5

# Variables
player_velocity = [0, 0]
player_position = [0, 0]
extra_jumps_left = extra_jumps
jump_cooldown_remaining = 0
game_is_running = True
previous_time = time()

# Start pygame
pygame.init()

# Create a 500px by 500px window
window = pygame.display.set_mode((500, 500))

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

    # Decrement jump cooldown
    if jump_cooldown_remaining > 0:
        jump_cooldown_remaining -= delta_time
    elif jump_cooldown_remaining < 0:
        jump_cooldown_remaining = 0

    # Loop over events that have happened
    for event in pygame.event.get():

        # When close button pressed, stop game loop
        if event.type == pygame.QUIT:
            game_is_running = False

    keys = pygame.key.get_pressed()

    # Movement left
    if keys[pygame.K_LEFT]:
        player_velocity[0] -= player_walk_speed * delta_time
    # Movement right
    if keys[pygame.K_RIGHT]:
        player_velocity[0] += player_walk_speed * delta_time

    # Jumping
    def jump():
        # Player Y position is from the top of the screen down, so subtracting makes it go up
        player_velocity[1] -= player_jump_height * delta_time

    # Make sure that the jump key is pressed and the jump cooldown is done
    if keys[pygame.K_UP] and jump_cooldown_remaining == 0:
        jump_cooldown_remaining = jump_cooldown
        # Make sure the player is on the ground before allowing them to jump
        if player_position[1] == window.get_height()-player_height:
            jump()
            # Reset extra jumps counter becuase the player touched the ground
            extra_jumps_left = extra_jumps

            # Reset jump cooldown because player is on the ground
            jump_cooldown = 0

        # If the player isn't on the ground bu still has extra jumps left
        elif extra_jumps_left > 0:
            jump()
            # Decrement the extra jumps counter
            extra_jumps_left -= 1

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

    # Clear window
    window.fill((0, 0, 0))

    # Draw the player
    pygame.draw.rect(window, player_colour,
                     (player_position[0], player_position[1], player_width, player_height))

    # Render all changes
    pygame.display.update()


# Stop game
pygame.quit()
