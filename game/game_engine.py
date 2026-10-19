"""
GameEngine: owns game state, collectibles, obstacles, timer, and lives.
"""

import random
import time
import pygame

from game.player import Player
from game.coin import Coin
from game.collection import check_collection
from game.renderer import WIDTH, HEIGHT

NUM_COINS = 6
ROUND_SECONDS = 30
STARTING_LIVES = 3

COIN_TYPES = (
    ("bronze", 1, (184, 115, 51)),
    ("silver", 3, (192, 192, 192)),
    ("gold", 5, (255, 215, 0)),
)


class GameEngine:
    def __init__(self):
        self._make_obstacles()
        self.reset()

    def _make_obstacles(self):
        # Fixed, visible rectangles. Keep them away from the starting centre.
        self.obstacles = [
            pygame.Rect(105, 105, 105, 24),
            pygame.Rect(330, 85, 24, 115),
            pygame.Rect(475, 205, 115, 24),
            pygame.Rect(205, 350, 24, 95),
            pygame.Rect(405, 365, 105, 24),
        ]

    def reset(self):
        """Start a fresh round and reset all round-specific state."""
        self.player = Player(x=WIDTH / 2, y=HEIGHT / 2)
        self.score = 0
        self.lives = STARTING_LIVES
        self.time_limit = ROUND_SECONDS
        self.start_time = time.monotonic()
        self.game_over = False
        self.game_over_reason = ""
        self._overlapping_obstacles = set()
        self.coins = [self._random_coin() for _ in range(NUM_COINS)]

    def _random_coin(self):
        coin_type, value, color = random.choice(COIN_TYPES)
        # Avoid placing coins inside obstacles or directly on the player spawn.
        for _ in range(100):
            x = random.randint(30, WIDTH - 30)
            y = random.randint(45, HEIGHT - 30)
            candidate = Coin(
                x=x, y=y, radius=12, value=value, color=color,
                coin_type=coin_type,
            )
            if candidate.get_rect().collidelist(self.obstacles) == -1:
                if not candidate.get_rect().colliderect(self.player.get_rect()):
                    return candidate
        # Extremely unlikely fallback if random placement keeps failing.
        return candidate

    @property
    def time_remaining(self):
        if self.game_over:
            return max(0, self._time_remaining_at_end)
        return max(0, self.time_limit - (time.monotonic() - self.start_time))

    def handle_input(self, keys_pressed):
        if self.game_over:
            return
        dx = dy = 0
        if keys_pressed[pygame.K_UP]:
            dy -= self.player.speed
        if keys_pressed[pygame.K_DOWN]:
            dy += self.player.speed
        if keys_pressed[pygame.K_LEFT]:
            dx -= self.player.speed
        if keys_pressed[pygame.K_RIGHT]:
            dx += self.player.speed
        self.player.move(dx, dy, WIDTH, HEIGHT)

    def update(self):
        if self.game_over:
            return

        remaining = self.time_limit - (time.monotonic() - self.start_time)
        if remaining <= 0:
            self._end_round("Time's up!", remaining=0)
            return

        # Award each collected coin once and remove it from the active list.
        collected = check_collection(self.player, self.coins)
        if collected:
            self.score += sum(coin.value for coin in collected)
            collected_ids = {id(coin) for coin in collected}
            self.coins = [
                coin for coin in self.coins if id(coin) not in collected_ids
            ]

        # One life per distinct contact. Remaining inside an obstacle does not
        # repeatedly remove lives; leaving and touching it again is a new event.
        player_rect = self.player.get_rect()
        current_overlaps = {
            index for index, obstacle in enumerate(self.obstacles)
            if player_rect.colliderect(obstacle)
        }
        new_contacts = current_overlaps - self._overlapping_obstacles
        if new_contacts:
            self.lives = max(0, self.lives - len(new_contacts))
        self._overlapping_obstacles = current_overlaps

        if self.lives <= 0:
            self._end_round("Out of lives!", remaining=remaining)

    def _end_round(self, reason, remaining=None):
        if remaining is None:
            remaining = self.time_limit - (time.monotonic() - self.start_time)
        self._time_remaining_at_end = max(0, remaining)
        self.game_over = True
        self.game_over_reason = reason

    def draw(self, surface, font):
        from game import renderer

        renderer.draw_scene(
            surface, self.player, self.coins, obstacles=self.obstacles
        )
        renderer.draw_text(surface, font, f"Score: {self.score}", (10, 8))
        renderer.draw_text(surface, font, f"Lives: {self.lives}", (10, 34))
        renderer.draw_text(
            surface, font, f"Time: {int(self.time_remaining + 0.999)}s",
            (WIDTH - 115, 8),
        )
        if self.game_over:
            renderer.draw_game_over(
                surface, font, self.game_over_reason, self.score
            )
