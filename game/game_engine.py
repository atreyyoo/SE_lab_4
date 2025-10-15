import pygame
import random
from .paddle import Paddle
from .ball import Ball

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class GameEngine:
    def __init__(self, width, height):
        # Initialize audio mixer first
        pygame.mixer.init()

        self.width = width
        self.height = height
        self.paddle_width = 10
        self.paddle_height = 100

        # Create paddles and ball
        self.player = Paddle(10, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ai = Paddle(width - 20, height // 2 - 50, self.paddle_width, self.paddle_height)
        self.ball = Ball(width // 2, height // 2, 7, 7, width, height)

        # Scores
        self.player_score = 0
        self.ai_score = 0
        self.font = pygame.font.SysFont("Arial", 30)

        # Game over and replay settings
        self.game_over = False
        self.winner_text = None
        self.winning_score = 5  # default

        # ---------------------------
        # Load Sound Effects
        # ---------------------------
        try:
            self.sound_paddle = pygame.mixer.Sound("assets/paddle_hit.wav")
            self.sound_wall = pygame.mixer.Sound("assets/wall_bounce.wav")
            self.sound_score = pygame.mixer.Sound("assets/score.wav")
        except Exception as e:
            print("⚠️ Sound files not found or failed to load:", e)
            self.sound_paddle = None
            self.sound_wall = None
            self.sound_score = None

    # ---------------------------
    # Handle Player Input
    # ---------------------------
    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.player.move(-10, self.height)
        if keys[pygame.K_s]:
            self.player.move(10, self.height)

    # ---------------------------
    # Update Game Logic
    # ---------------------------
    def update(self):
        if self.game_over:
            return  # Stop updates when game over

        prev_vx, prev_vy = self.ball.velocity_x, self.ball.velocity_y  # store before moving

        self.ball.move()
        self.ball.check_collision(self.player, self.ai)

        # Detect wall bounce sound (y velocity flipped)
        if self.ball.velocity_y != prev_vy:
            self.play_sound(self.sound_wall)

        # Detect paddle hit (x velocity flipped, ball still in bounds)
        if self.ball.velocity_x != prev_vx and (0 < self.ball.x < self.width):
            self.play_sound(self.sound_paddle)

        # Scoring logic
        if self.ball.x <= 0:
            self.ai_score += 1
            self.ball.reset()
            self.play_sound(self.sound_score)
        elif self.ball.x >= self.width:
            self.player_score += 1
            self.ball.reset()
            self.play_sound(self.sound_score)

        # AI follows the ball
        self.ai.auto_track(self.ball, self.height)

        # Check if anyone won
        self.check_game_over()

    # ---------------------------
    # Play Sound Safely
    # ---------------------------
    def play_sound(self, sound):
        if sound:
            sound.play()

    # ---------------------------
    # Check Game Over Condition
    # ---------------------------
    def check_game_over(self):
        if self.player_score >= self.winning_score:
            self.game_over = True
            self.winner_text = "Player Wins!"
        elif self.ai_score >= self.winning_score:
            self.game_over = True
            self.winner_text = "AI Wins!"

    # ---------------------------
    # Render Everything
    # ---------------------------
    def render(self, screen):
        screen.fill(BLACK)

        # Draw paddles and ball
        pygame.draw.rect(screen, WHITE, self.player.rect())
        pygame.draw.rect(screen, WHITE, self.ai.rect())
        pygame.draw.ellipse(screen, WHITE, self.ball.rect())

        # Draw middle line
        pygame.draw.aaline(screen, WHITE, (self.width // 2, 0), (self.width // 2, self.height))

        # Draw scores
        player_text = self.font.render(str(self.player_score), True, WHITE)
        ai_text = self.font.render(str(self.ai_score), True, WHITE)
        screen.blit(player_text, (self.width // 4, 20))
        screen.blit(ai_text, (self.width * 3 // 4, 20))

        # If game is over, show winner and replay menu
        if self.game_over and self.winner_text:
            self.display_winner(screen)
            self.display_replay_options(screen)

    # ---------------------------
    # Display Winner Message
    # ---------------------------
    def display_winner(self, screen):
        large_font = pygame.font.SysFont("Arial", 60)
        text_surface = large_font.render(self.winner_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2 - 60))
        screen.blit(text_surface, text_rect)

    # ---------------------------
    # Display Replay Menu
    # ---------------------------
    def display_replay_options(self, screen):
        small_font = pygame.font.SysFont("Arial", 28)
        options = [
            "Press 3 for Best of 3",
            "Press 5 for Best of 5",
            "Press 7 for Best of 7",
            "Press ESC to Exit"
        ]
        for i, text in enumerate(options):
            text_surface = small_font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2 + i * 40))
            screen.blit(text_surface, text_rect)

        pygame.display.flip()
        self.wait_for_replay_input(screen)

    # ---------------------------
    # Wait for User Replay Input
    # ---------------------------
    def wait_for_replay_input(self, screen):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        quit()
                    elif event.key in [pygame.K_3, pygame.K_5, pygame.K_7]:
                        if event.key == pygame.K_3:
                            self.winning_score = 2  # Best of 3 → first to 2
                        elif event.key == pygame.K_5:
                            self.winning_score = 3  # Best of 5 → first to 3
                        elif event.key == pygame.K_7:
                            self.winning_score = 4  # Best of 7 → first to 4
                        self.reset_game()
                        waiting = False
            pygame.time.delay(100)

    # ---------------------------
    # Reset Game for Replay
    # ---------------------------
    def reset_game(self):
        self.player_score = 0
        self.ai_score = 0
        self.game_over = False
        self.winner_text = None
        self.ball.reset()
