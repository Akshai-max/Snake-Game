import random
from enum import Enum

import pygame


class Direction(Enum):
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


class SnakeGame:
    def __init__(self, width=640, height=480, block_size=20, speed=12, mode_label="HUMAN"):
        pygame.init()
        self.width = width
        self.height = height
        self.block_size = block_size
        self.speed = speed
        self.mode_label = mode_label
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.big_font = pygame.font.SysFont("arial", 42, bold=True)
        self.reset()

    def reset(self):
        self.direction = Direction.RIGHT
        x = self.width // 2
        y = self.height // 2
        self.head = (x, y)
        self.snake = [
            self.head,
            (x - self.block_size, y),
            (x - 2 * self.block_size, y),
        ]
        self.score = 0
        self.frame_count = 0
        self.food = None
        self.place_food()

    def place_food(self):
        cols = self.width // self.block_size
        rows = self.height // self.block_size
        while True:
            x = random.randint(0, cols - 1) * self.block_size
            y = random.randint(0, rows - 1) * self.block_size
            self.food = (x, y)
            if self.food not in self.snake:
                break

    def play_step(self, action=None):
        self.frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        if action is not None:
            self.move_ai(action)
        self.move()
        self.snake.insert(0, self.head)

        reward = -0.1
        game_over = False

        if self.is_collision() or self.frame_count > 100 * len(self.snake):
            game_over = True
            reward = -10
            self.update_ui()
            self.clock.tick(self.speed)
            return reward, game_over, self.score

        if self.head == self.food:
            self.score += 1
            reward = 10
            self.place_food()
        else:
            self.snake.pop()

        self.update_ui()
        self.clock.tick(self.speed)
        return reward, game_over, self.score

    def move_human(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN

        self.move()
        self.snake.insert(0, self.head)
        game_over = self.is_collision()

        if game_over:
            self.update_ui()
            self.clock.tick(self.speed)
            return True, self.score

        if self.head == self.food:
            self.score += 1
            self.place_food()
        else:
            self.snake.pop()

        self.update_ui()
        self.clock.tick(self.speed)
        return False, self.score

    def move_ai(self, action):
        directions = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        index = directions.index(self.direction)

        if action == 1:
            self.direction = directions[(index - 1) % 4]
        elif action == 2:
            self.direction = directions[(index + 1) % 4]

    def move(self):
        x, y = self.head
        if self.direction == Direction.RIGHT:
            x += self.block_size
        elif self.direction == Direction.LEFT:
            x -= self.block_size
        elif self.direction == Direction.DOWN:
            y += self.block_size
        elif self.direction == Direction.UP:
            y -= self.block_size
        self.head = (x, y)

    def is_collision(self, point=None):
        if point is None:
            point = self.head
        x, y = point
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return point in self.snake[1:]

    def update_ui(self):
        self.display.fill((18, 18, 22))

        for part in self.snake:
            pygame.draw.rect(self.display, (44, 176, 83), (*part, self.block_size, self.block_size))
            pygame.draw.rect(self.display, (28, 125, 58), (*part, self.block_size, self.block_size), 1)

        pygame.draw.rect(self.display, (230, 68, 68), (*self.food, self.block_size, self.block_size))

        score_text = self.font.render(f"Score: {self.score}", True, (240, 240, 240))
        mode_text = self.font.render(self.mode_label, True, (165, 210, 255))
        self.display.blit(score_text, (12, 10))
        self.display.blit(mode_text, (self.width - mode_text.get_width() - 12, 10))
        pygame.display.flip()

    def show_game_over(self):
        while True:
            self.display.fill((18, 18, 22))
            title = self.big_font.render("Game Over", True, (245, 245, 245))
            score = self.font.render(f"Final Score: {self.score}", True, (230, 230, 230))
            hint = self.font.render("Press Enter for menu or Esc to quit", True, (180, 180, 180))
            self.display.blit(title, title.get_rect(center=(self.width // 2, self.height // 2 - 55)))
            self.display.blit(score, score.get_rect(center=(self.width // 2, self.height // 2)))
            self.display.blit(hint, hint.get_rect(center=(self.width // 2, self.height // 2 + 45)))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        raise SystemExit
