from cmath import rect
import pygame

gravity = 10
drag = 2

player_height = 20
player_width = 10
player_colour = (255, 0, 0)
player_jump_height = 5
player_walk_speed = 3
player_velocity = [0, 0]
player_position = [0, 0]
player_max_speed = [15, 30]


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
game_is_running = True
while game_is_running:
    # Sleep for 100 ms
    pygame.time.delay(50)

    # Loop over events that have happened
    for event in pygame.event.get():

        # When close button pressed, stop game loop
        if event.type == pygame.QUIT:
            game_is_running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_RIGHT]:
        player_velocity[0] += player_walk_speed
    if keys[pygame.K_LEFT]:
        player_velocity[0] -= player_walk_speed
    if keys[pygame.K_UP]:
        # Player Y position is from the top of the screen down, so subtracting makes it go up
        player_velocity[1] -= player_jump_height

    # Apply gravity
    # Player Y position is from the top of the screen down, so adding makes it go down
    player_velocity[1] += gravity

    # Apply drag
    if player_velocity[0] > 0:
        player_velocity[0] -= drag
    elif player_velocity[0] < 0:
        player_velocity[0] += drag

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
    if player_position[1]-player_height < window.get_height():
        player_position[1] = window.get_height()-player_height

    # Clear window
    window.fill((0, 0, 0))

    # Draw the player
    pygame.draw.rect(window, player_colour,
                     (player_position[0], player_position[1], player_width, player_height))
    pygame.display.update()


# Stop game
pygame.quit()
