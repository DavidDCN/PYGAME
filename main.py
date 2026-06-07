
import pygame
import random
import math
import os
from pygame import mixer

# ─────────────────────────────────────────────────────────
# INITIALISATION
# ─────────────────────────────────────────────────────────
pygame.init()

SCREEN_W, SCREEN_H = 800, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Space Invaders — Enhanced Edition")
clock = pygame.time.Clock()
FPS = 60  # frames per second cap

# ─────────────────────────────────────────────────────────
# COLOURS  (R, G, B)
# ─────────────────────────────────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GREEN      = (0,   255, 0)
YELLOW     = (255, 220, 0)
RED        = (255, 50,  50)
CYAN       = (0,   200, 255)
ORANGE     = (255, 140, 0)
PURPLE     = (180, 0,   255)
DARK_BG    = (5,   5,   20)   # fallback background colour

# ─────────────────────────────────────────────────────────
# ASSET LOADER HELPERS
# These functions try to load an asset and fall back to a
# coloured placeholder surface so the game never crashes
# when an asset file is missing.
# ─────────────────────────────────────────────────────────
def load_image(path, fallback_color=WHITE, size=(64, 64)):
    """Load an image, or return a solid-colour surface as fallback."""
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    # Fallback: coloured rectangle
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(fallback_color)
    return surf

def load_sound(path):
    """Load a sound file, or return None if missing."""
    if os.path.exists(path):
        return mixer.Sound(path)
    return None  # callers must check for None before playing

# ─────────────────────────────────────────────────────────
# LOAD ASSETS
# ─────────────────────────────────────────────────────────
# --- Background ---
background = load_image('5464956.jpg', DARK_BG, (SCREEN_W, SCREEN_H))

# --- Sprites ---
playerImg  = load_image('player.png',  CYAN,   (64, 64))
enemyImg   = load_image('enemy.png',   RED,    (48, 48))
bulletImg  = load_image('bullet.png',  YELLOW, (16, 32))
coinImg    = load_image('coin.png',    YELLOW, (28, 28))

# Boss ship — reuse enemy image but tinted/scaled larger
bossImg    = load_image('enemy.png',   PURPLE, (96, 64))

# --- Sounds ---
mixer.music.load('background.mp3') if os.path.exists('background.mp3') else None
if os.path.exists('background.mp3'):
    mixer.music.play(-1)   # -1 = loop forever

laser_sound     = load_sound('laser.mp3')
explosion_sound = load_sound('explode.mp3')
coin_sound      = load_sound('coin.mp3')        # optional; silent if missing

# ─────────────────────────────────────────────────────────
# FONTS
# ─────────────────────────────────────────────────────────
font_path_reg  = 'font/OpenSans-Regular.ttf'
font_path_bold = 'font/OpenSans-Bold.ttf'

# Fall back to pygame's default if custom font files are missing
try:
    hud_font    = pygame.font.Font(font_path_reg,  28)
    big_font    = pygame.font.Font(font_path_bold, 54)
    medium_font = pygame.font.Font(font_path_bold, 36)
except FileNotFoundError:
    hud_font    = pygame.font.SysFont('arial', 28)
    big_font    = pygame.font.SysFont('arial', 54, bold=True)
    medium_font = pygame.font.SysFont('arial', 36, bold=True)

# ─────────────────────────────────────────────────────────
# GAME CONSTANTS
# ─────────────────────────────────────────────────────────
ENEMY_COUNT          = 6      # enemies alive at once
KILLS_PER_BOSS_WAVE  = 20     # kills before Mother Ship appears
BOSS_MAX_HP          = 10     # hits needed to defeat the Mother Ship
COIN_LIFETIME        = 300    # frames a coin stays on screen (~5 sec)
PLAYER_SPEED_BASE    = 5.0    # player horizontal speed
ENEMY_BASE_SPEED     = 0.4    # starting horizontal speed for enemies
BULLET_SPEED         = 7      # pixels per frame bullet travels upward

# ─────────────────────────────────────────────────────────
# GAME STATE  — everything lives in one dict for clarity
# ─────────────────────────────────────────────────────────
def new_game_state():
    """Return a fresh game-state dict. Call this to (re)start."""
    return {
        # --- Player ---
        'playerX': 370,
        'playerY': 480,
        'playerX_change': 0,

        # --- Bullet ---
        'bulletX': 0,
        'bulletY': 480,
        'bullet_state': 'Ready',   # 'Ready' or 'Fire'

        # --- Score / Progression ---
        'score': 0,
        'coins': 0,            # collected coin count
        'total_kills': 0,      # lifetime alien kill counter
        'wave': 1,             # current wave number

        # --- Boss ---
        'boss_active': False,
        'bossX': SCREEN_W // 2 - 48,
        'bossY': -80,
        'bossX_change': 1.5,
        'bossY_target': 60,    # Y the boss descends to
        'boss_hp': BOSS_MAX_HP,

        # --- Enemies  (lists, one entry per enemy slot) ---
        'enemyX':        [random.randint(0,  752) for _ in range(ENEMY_COUNT)],
        'enemyY':        [random.randint(20,  80) for _ in range(ENEMY_COUNT)],
        'enemyX_change': [ENEMY_BASE_SPEED       for _ in range(ENEMY_COUNT)],
        'enemyY_change': [40                     for _ in range(ENEMY_COUNT)],
        # zig-zag phase angle per enemy (radians)
        'enemyZigAngle': [random.uniform(0, math.pi * 2) for _ in range(ENEMY_COUNT)],
        'enemyAlive':    [True                   for _ in range(ENEMY_COUNT)],

        # --- Coins on screen ---
        # Each coin: {'x', 'y', 'vy' (fall speed), 'lifetime'}
        'coins_on_screen': [],

        # --- Flags ---
        'game_over': False,
        'paused': False,
        'boss_defeated_flash': 0,   # countdown for flash effect after boss dies
    }

state = new_game_state()

# ─────────────────────────────────────────────────────────
# HELPER — distance between two points
# ─────────────────────────────────────────────────────────
def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

# ─────────────────────────────────────────────────────────
# DRAW FUNCTIONS
# ─────────────────────────────────────────────────────────
def draw_player(x, y):
    screen.blit(playerImg, (x, y))

def draw_enemy(x, y):
    screen.blit(enemyImg, (x, y))

def draw_boss(x, y):
    screen.blit(bossImg, (x, y))

def draw_bullet(x, y):
    screen.blit(bulletImg, (x + 24, y + 10))  # centred on ship

def draw_coin(x, y):
    screen.blit(coinImg, (x, y))

def draw_hud(s):
    """Draw score, coins, and wave info at the top of the screen."""
    score_surf = hud_font.render(f"Score: {s['score']}", True, GREEN)
    coin_surf  = hud_font.render(f"Coins: {s['coins']}",  True, YELLOW)
    wave_surf  = hud_font.render(f"Wave:  {s['wave']}",   True, CYAN)
    screen.blit(score_surf, (10,  10))
    screen.blit(coin_surf,  (10,  42))
    screen.blit(wave_surf,  (10,  74))

    # Kill progress bar towards next boss (bottom of HUD area)
    kills_in_wave  = s['total_kills'] % KILLS_PER_BOSS_WAVE
    bar_w = 200
    bar_h = 10
    bar_x, bar_y = SCREEN_W - bar_w - 10, 10
    # Background bar
    pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
    # Fill
    fill = int((kills_in_wave / KILLS_PER_BOSS_WAVE) * bar_w)
    pygame.draw.rect(screen, ORANGE, (bar_x, bar_y, fill, bar_h), border_radius=5)
    label = hud_font.render("Boss →", True, ORANGE)
    screen.blit(label, (bar_x - label.get_width() - 8, bar_y - 4))

def draw_boss_hp(s):
    """Draw boss health bar when boss is active."""
    bar_w = 300
    bar_h = 18
    bar_x = (SCREEN_W - bar_w) // 2
    bar_y = SCREEN_H - 36
    pygame.draw.rect(screen, (80, 0, 0),  (bar_x, bar_y, bar_w, bar_h), border_radius=6)
    fill = int((s['boss_hp'] / BOSS_MAX_HP) * bar_w)
    pygame.draw.rect(screen, RED, (bar_x, bar_y, fill, bar_h), border_radius=6)
    label = medium_font.render("MOTHER SHIP", True, RED)
    screen.blit(label, ((SCREEN_W - label.get_width()) // 2, bar_y - 32))

def draw_game_over():
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    txt  = big_font.render("GAME OVER", True, RED)
    txt2 = medium_font.render("Press R to restart  |  ESC to quit", True, WHITE)
    screen.blit(txt,  ((SCREEN_W - txt.get_width())  // 2, 220))
    screen.blit(txt2, ((SCREEN_W - txt2.get_width()) // 2, 300))

def draw_pause():
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))
    txt  = big_font.render("PAUSED", True, CYAN)
    txt2 = medium_font.render("Press P to resume", True, WHITE)
    screen.blit(txt,  ((SCREEN_W - txt.get_width())  // 2, 230))
    screen.blit(txt2, ((SCREEN_W - txt2.get_width()) // 2, 310))

def draw_boss_warning():
    """Flashing warning before the boss arrives."""
    txt = big_font.render("⚠  MOTHER SHIP INCOMING  ⚠", True, RED)
    screen.blit(txt, ((SCREEN_W - txt.get_width()) // 2, SCREEN_H // 2 - 30))

def draw_boss_defeated_flash(alpha):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((180, 0, 255, alpha))
    screen.blit(overlay, (0, 0))
    txt = big_font.render("BOSS DEFEATED!", True, WHITE)
    screen.blit(txt, ((SCREEN_W - txt.get_width()) // 2, SCREEN_H // 2 - 30))

# ─────────────────────────────────────────────────────────
# GAME LOGIC HELPERS
# ─────────────────────────────────────────────────────────
def get_wave_speed_multiplier(wave):
    """Each wave increases enemy speed by 20% capped at 3×."""
    return min(1.0 + (wave - 1) * 0.20, 3.0)

def respawn_enemy(s, i):
    """Reset a single enemy slot to a fresh random position at the top."""
    spd = ENEMY_BASE_SPEED * get_wave_speed_multiplier(s['wave'])
    s['enemyX'][i]        = random.randint(0, 752)
    s['enemyY'][i]        = random.randint(20, 80)
    s['enemyX_change'][i] = spd * random.choice([-1, 1])
    s['enemyZigAngle'][i] = random.uniform(0, math.pi * 2)
    s['enemyAlive'][i]    = True

def spawn_coin(s, x, y):
    """Drop a coin at (x, y) — it falls slowly down the screen."""
    s['coins_on_screen'].append({
        'x': x + 10,
        'y': y,
        'vy': 1.5,              # fall speed (pixels/frame)
        'lifetime': COIN_LIFETIME
    })

def start_boss_wave(s):
    """Activate the boss. Hide all regular enemies temporarily."""
    s['boss_active']  = True
    s['bossX']        = SCREEN_W // 2 - 48
    s['bossY']        = -80
    s['bossX_change'] = 1.5 * get_wave_speed_multiplier(s['wave'])
    s['boss_hp']      = BOSS_MAX_HP + (s['wave'] - 1) * 2  # harder each wave
    # Push all enemies off screen until boss is defeated
    for i in range(ENEMY_COUNT):
        s['enemyY'][i]    = 2000
        s['enemyAlive'][i] = False

def end_boss_wave(s):
    """Called when the boss is defeated. Begin next wave."""
    s['boss_active']         = False
    s['wave']               += 1
    s['boss_defeated_flash'] = 90   # frames to show flash (1.5 sec at 60fps)
    # Respawn all enemies for the new wave
    for i in range(ENEMY_COUNT):
        respawn_enemy(s, i)

# ─────────────────────────────────────────────────────────
# UPDATE FUNCTIONS  (called every frame while not paused)
# ─────────────────────────────────────────────────────────
def update_player(s):
    s['playerX'] += s['playerX_change']
    # Clamp to screen boundaries (sprite is 64px wide)
    s['playerX'] = max(0, min(s['playerX'], SCREEN_W - 64))

def update_enemies(s):
    """Move enemies with zig-zag motion and check game-over condition."""
    spd = ENEMY_BASE_SPEED * get_wave_speed_multiplier(s['wave'])

    for i in range(ENEMY_COUNT):
        if not s['enemyAlive'][i]:
            continue

        # --- Horizontal movement ---
        s['enemyX'][i] += s['enemyX_change'][i]

        # Bounce off walls, descend one step
        if s['enemyX'][i] <= 0:
            s['enemyX_change'][i] = abs(spd)
            s['enemyY'][i]       += s['enemyY_change'][i]
        elif s['enemyX'][i] >= SCREEN_W - 48:
            s['enemyX_change'][i] = -abs(spd)
            s['enemyY'][i]       += s['enemyY_change'][i]

        # --- Zig-zag (sinusoidal vertical wobble) ---
        s['enemyZigAngle'][i] += 0.07   # advance phase
        zig_offset = math.sin(s['enemyZigAngle'][i]) * 18
        draw_y = s['enemyY'][i] + zig_offset   # visual only; base Y unchanged

        # --- Game-over check (enemy reaches player row) ---
        if s['enemyY'][i] > SCREEN_H - 80:
            s['game_over'] = True
            return  # stop processing immediately

        # Draw the enemy at its zig-zag position
        draw_enemy(s['enemyX'][i], draw_y)

def update_bullet(s):
    """Move bullet upward and check for enemy/boss collisions."""
    if s['bullet_state'] != 'Fire':
        return

    draw_bullet(s['bulletX'], s['bulletY'])
    s['bulletY'] -= BULLET_SPEED

    # Bullet exits top of screen → reset
    if s['bulletY'] <= 0:
        s['bulletY']      = 480
        s['bullet_state'] = 'Ready'
        return

    # --- Check collision with regular enemies ---
    for i in range(ENEMY_COUNT):
        if not s['enemyAlive'][i]:
            continue
        if distance(s['enemyX'][i] + 24, s['enemyY'][i] + 24,
                    s['bulletX'] + 32,   s['bulletY'] + 16) < 35:
            # Hit!
            if explosion_sound:
                explosion_sound.play()
            spawn_coin(s, s['enemyX'][i], s['enemyY'][i])
            s['score']       += 10
            s['total_kills'] += 1
            s['bulletY']      = 480
            s['bullet_state'] = 'Ready'
            s['enemyAlive'][i] = False  # mark dead; respawn next frame
            respawn_enemy(s, i)

            # Check if it's time to spawn the boss
            if s['total_kills'] > 0 and s['total_kills'] % KILLS_PER_BOSS_WAVE == 0:
                start_boss_wave(s)
            return

    # --- Check collision with boss ---
    if s['boss_active']:
        if distance(s['bossX'] + 48, s['bossY'] + 32,
                    s['bulletX'] + 32, s['bulletY'] + 16) < 60:
            if explosion_sound:
                explosion_sound.play()
            s['boss_hp']      -= 1
            s['score']        += 50
            s['bulletY']       = 480
            s['bullet_state']  = 'Ready'

            if s['boss_hp'] <= 0:
                # Drop a big coin reward
                for _ in range(5):
                    spawn_coin(s,
                               s['bossX'] + random.randint(-30, 30),
                               s['bossY'])
                end_boss_wave(s)
            return

def update_boss(s):
    """Move the Mother Ship horizontally. It descends to bossY_target."""
    if not s['boss_active']:
        return

    # Descend until reaching target Y
    if s['bossY'] < s['bossY_target']:
        s['bossY'] += 1.5

    # Horizontal bounce
    s['bossX'] += s['bossX_change']
    if s['bossX'] <= 0 or s['bossX'] >= SCREEN_W - 96:
        s['bossX_change'] *= -1

    draw_boss(s['bossX'], s['bossY'])
    draw_boss_hp(s)

def update_coins(s):
    """Move coins downward, check player collection, expire old coins."""
    player_rect = pygame.Rect(s['playerX'], s['playerY'], 64, 64)
    surviving   = []

    for coin in s['coins_on_screen']:
        coin['y']        += coin['vy']
        coin['lifetime'] -= 1

        if coin['lifetime'] <= 0 or coin['y'] > SCREEN_H:
            continue  # coin expired or fell off screen

        coin_rect = pygame.Rect(coin['x'], coin['y'], 28, 28)
        if player_rect.colliderect(coin_rect):
            # Player collected the coin
            s['coins'] += 1
            s['score'] += 5
            if coin_sound:
                coin_sound.play()
        else:
            draw_coin(coin['x'], coin['y'])
            surviving.append(coin)

    s['coins_on_screen'] = surviving

# ─────────────────────────────────────────────────────────
# MAIN GAME LOOP
# ─────────────────────────────────────────────────────────
# Boss warning flicker timer (counts down before boss spawns)
boss_warning_timer = 0

running = True
while running:
    clock.tick(FPS)  # cap to 60 FPS

    # ── EVENT HANDLING ────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # --- Quit ---
            if event.key == pygame.K_ESCAPE:
                running = False

            # --- Restart after game over ---
            if event.key == pygame.K_r and state['game_over']:
                state = new_game_state()

            # --- Pause / Resume (P key) ---
            if event.key == pygame.K_p and not state['game_over']:
                state['paused'] = not state['paused']

            if not state['paused'] and not state['game_over']:
                # --- Player movement ---
                if event.key == pygame.K_LEFT:
                    state['playerX_change'] = -PLAYER_SPEED_BASE
                if event.key == pygame.K_RIGHT:
                    state['playerX_change'] = PLAYER_SPEED_BASE

                # --- Shoot bullet ---
                if event.key == pygame.K_SPACE:
                    if state['bullet_state'] == 'Ready':
                        if laser_sound:
                            laser_sound.play()
                        state['bulletX']      = state['playerX']
                        state['bulletY']      = state['playerY']
                        state['bullet_state'] = 'Fire'

        if event.type == pygame.KEYUP:
            # Stop player when key released
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                state['playerX_change'] = 0

    # ── DRAW BACKGROUND ──────────────────────────────────
    screen.blit(background, (0, 0))

    # ── PAUSED STATE ─────────────────────────────────────
    if state['paused']:
        draw_hud(state)
        draw_player(state['playerX'], state['playerY'])
        draw_pause()
        pygame.display.update()
        continue   # skip all update logic while paused

    # ── GAME OVER STATE ───────────────────────────────────
    if state['game_over']:
        draw_hud(state)
        draw_game_over()
        pygame.display.update()
        continue

    # ── ACTIVE GAMEPLAY ───────────────────────────────────

    # Boss-defeated flash overlay (fades out)
    if state['boss_defeated_flash'] > 0:
        alpha = int((state['boss_defeated_flash'] / 90) * 200)
        draw_boss_defeated_flash(alpha)
        state['boss_defeated_flash'] -= 2
    
    # Update and draw all game objects
    update_player(state)
    update_enemies(state)   # also draws enemies
    update_bullet(state)    # also draws bullet
    update_boss(state)      # also draws boss
    update_coins(state)     # also draws coins

    # Draw player last so it appears on top
    draw_player(state['playerX'], state['playerY'])

    # Draw HUD over everything
    draw_hud(state)

    # ── REFRESH DISPLAY ──────────────────────────────────
    pygame.display.update()

# ─────────────────────────────────────────────────────────
# CLEAN EXIT
# ─────────────────────────────────────────────────────────
pygame.quit()