import pygame

from agent import QAgent
from game import SnakeGame


WIDTH = 640
HEIGHT = 480
BLOCK_SIZE = 20
HUMAN_SPEED = 12
AI_SPEED = 40
EPISODES = 750


def draw_menu(screen, font, big_font):
    screen.fill((18, 18, 22))
    title = big_font.render("Snake Game", True, (245, 245, 245))
    human = font.render("Press 1 - Human Mode", True, (225, 225, 225))
    ai = font.render("Press 2 - AI Mode", True, (225, 225, 225))
    quit_text = font.render("Press Esc - Quit", True, (170, 170, 170))

    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 90)))
    screen.blit(human, human.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
    screen.blit(ai, ai.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 25)))
    screen.blit(quit_text, quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80)))
    pygame.display.flip()


def menu():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")
    font = pygame.font.SysFont("arial", 26)
    big_font = pygame.font.SysFont("arial", 48, bold=True)
    clock = pygame.time.Clock()

    while True:
        draw_menu(screen, font, big_font)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "human"
                if event.key == pygame.K_2:
                    return "ai"
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    raise SystemExit
        clock.tick(30)


def run_human():
    game = SnakeGame(WIDTH, HEIGHT, BLOCK_SIZE, HUMAN_SPEED, "HUMAN")
    while True:
        game_over, score = game.move_human()
        if game_over:
            print(f"Human game over | Score: {score}")
            game.show_game_over()
            return


def run_ai():
    agent = QAgent()
    game = SnakeGame(WIDTH, HEIGHT, BLOCK_SIZE, AI_SPEED, "AI")
    best_score = 0

    for episode in range(1, EPISODES + 1):
        game.reset()
        done = False

        while not done:
            state = agent.get_state(game)
            action = agent.get_action(state)
            reward, done, score = game.play_step(action)
            next_state = agent.get_state(game)
            agent.train_step(state, action, reward, next_state, done)

        best_score = max(best_score, score)
        agent.decay_epsilon()
        print(
            f"Episode: {episode}/{EPISODES} | "
            f"Score: {score} | Best: {best_score} | Epsilon: {agent.epsilon:.3f}"
        )

        if episode % 50 == 0:
            agent.save()

    agent.save()
    print(f"Training complete | Best score: {best_score}")
    game.show_game_over()


def main():
    while True:
        selected_mode = menu()
        if selected_mode == "human":
            run_human()
        elif selected_mode == "ai":
            run_ai()


if __name__ == "__main__":
    main()
