import pygame
import sys
import random
import math

# ── Constants ────────────────────────────────────────────────────────────────
WINDOW_WIDTH  = 800
WINDOW_HEIGHT = 600
FPS           = 60
WINNING_SCORE = 7

# Colors (dark background, bright contrasting elements)
COLOR_BG        = (15,  15,  30)   # very dark navy
COLOR_PLAYER    = (0,  220, 255)   # cyan
COLOR_COMPUTER  = (255,  80,  80)  # red-orange
COLOR_BALL      = (255, 230,  50)  # yellow
COLOR_NET       = (60,   60,  90)  # muted purple-grey
COLOR_TEXT      = (220, 220, 220)  # light grey
COLOR_WIN_TEXT  = (255, 215,   0)  # gold

PADDLE_WIDTH  = 12
PADDLE_HEIGHT = 90
PADDLE_SPEED  = 6
BALL_SIZE      = 14
BALL_SPEED_INIT = 5

# Computer AI difficulty: fraction of max speed the AI actually moves (0-1)
AI_SPEED_FACTOR = 0.82


# ── Helper classes ────────────────────────────────────────────────────────────
class Paddle:
    def __init__(self, x, y, color):
        self.rect  = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.color = color
        self.speed = PADDLE_SPEED

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)

    def move_up(self):
        self.rect.y = max(0, self.rect.y - self.speed)

    def move_down(self):
        self.rect.y = min(WINDOW_HEIGHT - PADDLE_HEIGHT, self.rect.y + self.speed)

    def clamp(self):
        self.rect.y = max(0, min(WINDOW_HEIGHT - PADDLE_HEIGHT, self.rect.y))


class Ball:
    def __init__(self):
        self.rect  = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.color = COLOR_BALL
        self.reset()

    def reset(self):
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        angle = random.uniform(-45, 45)
        direction = random.choice([-1, 1])
        rad = math.radians(angle)
        self.vx = direction * BALL_SPEED_INIT * math.cos(rad)
        self.vy = BALL_SPEED_INIT * math.sin(rad)

    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, self.rect)

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)

        # Bounce off top / bottom walls
        if self.rect.top <= 0:
            self.rect.top = 0
            self.vy = abs(self.vy)
        elif self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.vy = -abs(self.vy)

    def bounce_off_paddle(self, paddle):
        """Reflect the ball and slightly increase speed, angling based on hit position."""
        # Relative hit position on paddle: -1 (top) to +1 (bottom)
        relative_y = (self.rect.centery - paddle.rect.centery) / (PADDLE_HEIGHT / 2)
        relative_y = max(-1.0, min(1.0, relative_y))

        bounce_angle = relative_y * 60  # max 60° from horizontal
        rad = math.radians(bounce_angle)

        speed = math.hypot(self.vx, self.vy) * 1.04  # 4 % speed increase
        speed = min(speed, BALL_SPEED_INIT * 2.5)     # cap at 2.5× initial speed

        # Flip horizontal direction
        new_vx = math.copysign(speed * math.cos(rad), -self.vx)
        self.vx = new_vx
        self.vy = speed * math.sin(rad)

    def check_scored(self):
        """Return 'computer' if ball left the screen left, 'player' if right, else None."""
        if self.rect.right < 0:
            return "computer"
        if self.rect.left > WINDOW_WIDTH:
            return "player"
        return None


# ── Main game function ────────────────────────────────────────────────────────
def draw_net(surface):
    segment_height = 20
    gap = 10
    x = WINDOW_WIDTH // 2 - 1
    y = 0
    while y < WINDOW_HEIGHT:
        pygame.draw.rect(surface, COLOR_NET, (x, y, 2, segment_height))
        y += segment_height + gap


def draw_scores(surface, font, player_score, computer_score):
    p_text = font.render(str(player_score),   True, COLOR_PLAYER)
    c_text = font.render(str(computer_score), True, COLOR_COMPUTER)
    surface.blit(p_text, (WINDOW_WIDTH // 4 - p_text.get_width() // 2, 20))
    surface.blit(c_text, (3 * WINDOW_WIDTH // 4 - c_text.get_width() // 2, 20))


def draw_labels(surface, small_font):
    p_label = small_font.render("PLAYER", True, COLOR_PLAYER)
    c_label = small_font.render("COMPUTER", True, COLOR_COMPUTER)
    surface.blit(p_label, (WINDOW_WIDTH // 4 - p_label.get_width() // 2, 70))
    surface.blit(c_label, (3 * WINDOW_WIDTH // 4 - c_label.get_width() // 2, 70))


def show_win_screen(surface, font, big_font, winner):
    surface.fill(COLOR_BG)
    msg  = "YOU WIN!" if winner == "player" else "COMPUTER WINS!"
    sub  = "Press SPACE to play again  |  ESC to quit"
    text = big_font.render(msg, True, COLOR_WIN_TEXT)
    sub_text = font.render(sub, True, COLOR_TEXT)
    surface.blit(text,     (WINDOW_WIDTH // 2 - text.get_width() // 2,
                             WINDOW_HEIGHT // 2 - text.get_height()))
    surface.blit(sub_text, (WINDOW_WIDTH // 2 - sub_text.get_width() // 2,
                             WINDOW_HEIGHT // 2 + 20))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pong – Player vs Computer")
    clock = pygame.time.Clock()

    score_font = pygame.font.SysFont("monospace", 52, bold=True)
    label_font = pygame.font.SysFont("monospace", 18)
    big_font   = pygame.font.SysFont("monospace", 64, bold=True)

    while True:  # outer loop – allows restart after a win
        player_score   = 0
        computer_score = 0

        player   = Paddle(30, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, COLOR_PLAYER)
        computer = Paddle(WINDOW_WIDTH - 30 - PADDLE_WIDTH,
                          WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, COLOR_COMPUTER)
        ball = Ball()

        game_over  = False
        winner     = None

        while not game_over:
            clock.tick(FPS)

            # ── Events ──────────────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            # ── Player input ─────────────────────────────────────────────────
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]   or keys[pygame.K_w]:
                player.move_up()
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                player.move_down()

            # ── Computer AI ──────────────────────────────────────────────────
            # Move toward the ball's centre, limited by AI speed
            target_y = ball.rect.centery - PADDLE_HEIGHT // 2
            diff = target_y - computer.rect.y
            ai_move = PADDLE_SPEED * AI_SPEED_FACTOR
            if abs(diff) > ai_move:
                computer.rect.y += ai_move if diff > 0 else -ai_move
            else:
                computer.rect.y = target_y
            computer.clamp()

            # ── Ball update ───────────────────────────────────────────────────
            ball.update()

            # Ball ↔ paddle collision
            if ball.vx < 0 and ball.rect.colliderect(player.rect):
                ball.rect.left = player.rect.right
                ball.bounce_off_paddle(player)

            if ball.vx > 0 and ball.rect.colliderect(computer.rect):
                ball.rect.right = computer.rect.left
                ball.bounce_off_paddle(computer)

            # Check for scoring
            scored = ball.check_scored()
            if scored == "computer":
                computer_score += 1
                ball.reset()
            elif scored == "player":
                player_score += 1
                ball.reset()

            # Check for win
            if player_score >= WINNING_SCORE:
                winner = "player"
                game_over = True
            elif computer_score >= WINNING_SCORE:
                winner = "computer"
                game_over = True

            # ── Draw ──────────────────────────────────────────────────────────
            screen.fill(COLOR_BG)
            draw_net(screen)
            draw_scores(screen, score_font, player_score, computer_score)
            draw_labels(screen, label_font)
            player.draw(screen)
            computer.draw(screen)
            ball.draw(screen)
            pygame.display.flip()

        # Show win screen and wait; if SPACE pressed restart outer loop
        show_win_screen(screen, label_font, big_font, winner)


if __name__ == "__main__":
    main()
