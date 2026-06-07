─────────────────────────────────────────────────────────────────
  THE STORY
─────────────────────────────────────────────────────────────────
  Alien drones pour through the galaxy, attacking in waves.
  Each drone you destroy drops a coin — catch it before it
  falls off screen for bonus points!
 
  Every 20 kills, the MOTHER SHIP descends. It takes 10 hits
  to destroy and bounces faster each wave. Beat the Mother
  Ship to advance to the next wave — but be warned, the aliens
  get faster and hungrier every time.
 
  How many waves can you survive?
 
 
─────────────────────────────────────────────────────────────────
  CONTROLS
─────────────────────────────────────────────────────────────────
  LEFT ARROW    Move spaceship left
  RIGHT ARROW   Move spaceship right
  SPACEBAR      Fire bullet
  P             Pause / Resume
  R             Restart (after Game Over)
  ESC           Quit game
 
 
─────────────────────────────────────────────────────────────────
  SCORING
─────────────────────────────────────────────────────────────────
  Kill a drone            +10 points
  Catch a coin             +5 points
  Hit the Mother Ship     +50 points per hit
  Boss defeat coin drop:   5 coins fall at once!
 
 
─────────────────────────────────────────────────────────────────
  WAVE SYSTEM
─────────────────────────────────────────────────────────────────
  Wave 1  →  Normal drone speed
  Wave 2  →  +20% speed
  Wave 3  →  +40% speed
  ...and so on, capped at 3× base speed.
 
  Mother Ship HP also increases each wave:
    Wave 1 Boss  →  10 HP
    Wave 2 Boss  →  12 HP
    Wave 3 Boss  →  14 HP  ... etc.
 
  The orange progress bar (top right) shows kills until next boss.
 
 
─────────────────────────────────────────────────────────────────
  GAME OVER
─────────────────────────────────────────────────────────────────
  The game ends if any alien drone reaches the bottom of the
  screen (your ship's row). Press R to restart.
 
 
─────────────────────────────────────────────────────────────────
  FILE STRUCTURE
─────────────────────────────────────────────────────────────────
  main.py              ← Main game script (run this)
  README.txt           ← This file
 
  Required assets (place all in the same folder as main.py):
  ┌──────────────────┬────────────────────────────────────────┐
  │ File             │ Description                            │
  ├──────────────────┼────────────────────────────────────────┤
  │ 5464956.jpg      │ Space background image                 │
  │ player.png       │ Player spaceship sprite (64×64)        │
  │ enemy.png        │ Alien drone sprite (48×48)             │
  │ bullet.png       │ Bullet sprite (16×32)                  │
  │ coin.png         │ Coin sprite (28×28)                    │
  │ background.mp3   │ Looping background music               │
  │ laser.mp3        │ Laser fire sound effect                │
  │ explode.mp3      │ Explosion sound effect                 │
  │ coin.mp3         │ (Optional) Coin pickup sound           │
  │ font/            │ Folder containing OpenSans fonts:      │
  │   OpenSans-Regular.ttf                                    │
  │   OpenSans-Bold.ttf                                       │
  └──────────────────┴────────────────────────────────────────┘
 
  NOTE: If any image or font file is missing, the game will
  use coloured placeholder shapes and still run normally.
 
 
─────────────────────────────────────────────────────────────────
  INSTALLATION & RUNNING
─────────────────────────────────────────────────────────────────
  1. Make sure Python 3 is installed:
       python --version
 
  2. Install pygame if you haven't already:
       pip install pygame
 
  3. Place all asset files (listed above) in the same folder
     as main.py.
 
  4. Run the game:
       python main.py
 
for bullet link
https://www.flaticon.com/free-icon/bullet_224681?term=bullet&page=1&position=3&origin=search&related_id=224681

player ship link
https://www.flaticon.com/free-icon/bullet_224681?term=bullet&page=1&position=3&origin=search&related_id=224681

enemy ship link
https://www.flaticon.com/free-icon/bullet_224681?term=bullet&page=1&position=3&origin=search&related_id=224681