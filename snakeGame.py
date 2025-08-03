import pygame
import random
import os

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 400
GRID_SIZE = 15
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE  # Fixed typo from GRID_HEIGHT
FPS = 8
WALL_OFFSET = 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = ( 9,255,42)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Sound initialization
try:
    pygame.mixer.init()
    eat_sound = pygame.mixer.Sound("eat.wav") if os.path.exists("eat.wav") else None
    crash_sound = pygame.mixer.Sound("crash.wav") if os.path.exists("crash.wav") else None
except:
    eat_sound = None
    crash_sound = None

class Snake:
    def __init__(self, x, y):
        self.body = [(x, y), (x-1, y), (x-2, y)]  # 3 segments at start
        self.direction = (1, 0)
        self.last_direction = self.direction
        self.growing = False
    
    def move(self):
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        self.body.insert(0, new_head)
        
        if not self.growing:
            self.body.pop()
        else:
            self.growing = False
            
        self.last_direction = self.direction
    
    def grow(self):
        self.growing = True
    
    def check_collision(self, food):
        return self.body[0] == (food.x, food.y)
    
    def draw(self, screen, grid_size):
        # Draw head
        head = self.body[0]
        pygame.draw.rect(screen, RED, 
                        (head[0] * grid_size, head[1] * grid_size, 
                         grid_size, grid_size), 0, 5)
        
        # Draw body
        for i, segment in enumerate(self.body[1:-1]):
            prev = self.body[i]
            next_seg = self.body[i+2]
            radius = 3 if (prev[0] != next_seg[0] and prev[1] != next_seg[1]) else 0
            pygame.draw.rect(screen, RED, 
                            (segment[0] * grid_size, segment[1] * grid_size, 
                             grid_size, grid_size), 0, radius)
        
        # Draw tail
        tail = self.body[-1]
        pygame.draw.rect(screen, RED, 
                        (tail[0] * grid_size, tail[1] * grid_size, 
                         grid_size, grid_size), 0, 3)

class Food:
    def __init__(self, grid_width, grid_height):
        self.x = random.randint(WALL_OFFSET, grid_width - 1 - WALL_OFFSET)
        self.y = random.randint(WALL_OFFSET, grid_height - 1 - WALL_OFFSET)
    
    def respawn(self, grid_width, grid_height, snake_body):
        while True:
            self.x = random.randint(WALL_OFFSET, grid_width - 1 - WALL_OFFSET)
            self.y = random.randint(WALL_OFFSET, grid_height - 1 - WALL_OFFSET)
            if (self.x, self.y) not in snake_body:
                break
    
    def draw(self, screen, grid_size):
        pygame.draw.rect(screen, BLACK, 
                        (self.x * grid_size, self.y * grid_size, 
                         grid_size, grid_size), 0, 5)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Nardos Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)  # Added font initialization
        self.reset()
        self.wall_rect = pygame.Rect(
            WALL_OFFSET * GRID_SIZE, 
            WALL_OFFSET * GRID_SIZE, 
            SCREEN_WIDTH - 2 * WALL_OFFSET * GRID_SIZE,  # Fixed calculation
            SCREEN_HEIGHT - 2 * WALL_OFFSET * GRID_SIZE   # Fixed calculation
        )
    
    def reset(self):
        self.snake = Snake(GRID_WIDTH // 2, GRID_HEIGHT // 2)
        self.food = Food(GRID_WIDTH, GRID_HEIGHT)
        self.score = 0
        self.game_over = False
    
    def draw_walls(self):
        pygame.draw.rect(self.screen, BLUE, self.wall_rect, 2)
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if not self.game_over:
                        if event.key == pygame.K_UP and self.snake.last_direction != (0, 1):
                            self.snake.direction = (0, -1)
                        elif event.key == pygame.K_DOWN and self.snake.last_direction != (0, -1):
                            self.snake.direction = (0, 1)
                        elif event.key == pygame.K_LEFT and self.snake.last_direction != (1, 0):
                            self.snake.direction = (-1, 0)
                        elif event.key == pygame.K_RIGHT and self.snake.last_direction != (-1, 0):
                            self.snake.direction = (1, 0)
                    if self.game_over:
                        self.reset()

            if not self.game_over:
                self.snake.move()
                
                # Food collision
                if self.snake.check_collision(self.food):
                    if eat_sound:
                        eat_sound.play()
                    self.score += 1
                    self.snake.grow()
                    self.food.respawn(GRID_WIDTH, GRID_HEIGHT, self.snake.body)
                
                # Wall collision
                head = self.snake.body[0]
                if (head[0] < WALL_OFFSET or head[0] >= GRID_WIDTH - WALL_OFFSET or
                    head[1] < WALL_OFFSET or head[1] >= GRID_HEIGHT - WALL_OFFSET):
                    if not self.game_over and crash_sound:
                        crash_sound.play()
                    self.game_over = True
                
                # Self collision
                if self.snake.body[0] in self.snake.body[1:]:
                    if not self.game_over and crash_sound:
                        crash_sound.play()
                    self.game_over = True

            # Drawing
            self.screen.fill(GREEN)
            self.draw_walls()
            self.snake.draw(self.screen, GRID_SIZE)
            self.food.draw(self.screen, GRID_SIZE)
            
            # Score display
            score_text = self.font.render(f'Score: {self.score}', True, BLACK)
            self.screen.blit(score_text, (7, 7))
            
            # Game over display
            if self.game_over:
                game_over_text = self.font.render('Game Over! Press ANY KEY to Restart', True, RED)
                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(game_over_text, text_rect)
            
            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()