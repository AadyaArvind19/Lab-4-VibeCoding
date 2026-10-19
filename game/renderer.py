"""
Renderer: all Pygame drawing lives here.
"""

import pygame

WIDTH, HEIGHT = 700, 500
WINDOW_SIZE = (WIDTH, HEIGHT)

COLOR_BG = (35, 45, 35)
COLOR_PLAYER = (80, 180, 255)
COLOR_TEXT = (255, 255, 255)
COLOR_OBSTACLE = (190, 75, 65)


def draw_scene(surface, player, coins, obstacles=None):
    surface.fill(COLOR_BG)
    if obstacles:
        for obstacle in obstacles:
            pygame.draw.rect(surface, COLOR_OBSTACLE, obstacle, border_radius=4)
    for coin in coins:
        pygame.draw.circle(
            surface, coin.color, (int(coin.x), int(coin.y)), coin.radius
        )
    pygame.draw.rect(surface, COLOR_PLAYER, player.get_rect(), border_radius=4)


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_banner(surface, font, text):
    surf = font.render(text, True, (255, 220, 80))
    rect = surf.get_rect(
        center=(surface.get_width() // 2, surface.get_height() // 2)
    )
    surface.blit(surf, rect)


def draw_game_over(surface, font, reason, score):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))
    surface.blit(overlay, (0, 0))

    title_font = pygame.font.SysFont("consolas", 36, bold=True)
    detail_font = pygame.font.SysFont("consolas", 23)
    title = title_font.render("GAME OVER", True, (255, 220, 80))
    reason_surface = detail_font.render(reason, True, COLOR_TEXT)
    score_surface = detail_font.render(f"Final score: {score}", True, COLOR_TEXT)
    restart_surface = detail_font.render("Press R to restart", True, COLOR_TEXT)

    center_x = surface.get_width() // 2
    surface.blit(title, title.get_rect(center=(center_x, 185)))
    surface.blit(reason_surface, reason_surface.get_rect(center=(center_x, 235)))
    surface.blit(score_surface, score_surface.get_rect(center=(center_x, 275)))
    surface.blit(restart_surface, restart_surface.get_rect(center=(center_x, 320)))
