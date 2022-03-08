import pygame

# Start pygame
pygame.init()

# Create a 500px by 500px window
window = pygame.display.set_mode((500, 500))

# Give window a title
pygame.display.set_caption("Glen Denham Simulator")

# Game loop
game_is_running = True
while game_is_running:
    # Sleep for 100 ms
    pygame.time.delay(100)

    # Loop over events that have happened
    for event in pygame.event.get():

        # When close button pressed, stop game loop
        if event.type == pygame.QUIT:
            game_is_running = False

# Stop game
pygame.quit()
