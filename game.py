#!/usr/bin/env python3

import json
import pygame
import sys

pygame.mixer.pre_init()
pygame.init()

# Window settings
TITLE = "Platformer"
WIDTH = 960
HEIGHT = 640
FPS = 60
GRID_SIZE = 64

# Options
sound_on = True

# Controls
LEFT = pygame.K_a
RIGHT = pygame.K_d
DOWN = pygame.K_s
JUMP = pygame.K_SPACE
SOUND_BUTTON = pygame.K_z
SHIFT = pygame.K_LSHIFT
PAUSE = pygame.K_p

# Levels
levels = ["levels/world-1.json"]

# Colors
TRANSPARENT = (0, 0, 0, 0)
DARK_BLUE = (16, 86, 103)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fonts
FONT_SM = pygame.font.Font("assets/fonts/minya_nouvelle_bd.ttf", 32)
FONT_MD = pygame.font.Font("assets/fonts/minya_nouvelle_bd.ttf", 64)
FONT_LG = pygame.font.Font("assets/fonts/thats_super.ttf", 72)

# Timer
clock = pygame.time.Clock()
refresh_rate = 60

# Helper functions
def load_image(file_path):
    img = pygame.image.load(file_path)
    img = pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))

    return img

    
def play_sound(sound, loops=0, maxtime=0, fade_ms=0):
    if sound_on:
        if maxtime == 0:
            sound.play(loops, maxtime, fade_ms)
        else:
            sound.play(loops, maxtime, fade_ms)
    

def play_music():
    if sound_on:
        pygame.mixer.music.play(-1)

 
# Images
hero_walk1 = load_image("assets/character/adventurer_walk1.png")
hero_walk2 = load_image("assets/character/adventurer_walk2.png")
hero_jump = load_image("assets/character/adventurer_jump.png")
hero_idle = load_image("assets/character/adventurer_idle.png")
hero_fall = load_image("assets/character/adventurer_fall.png")
hero_crouch = load_image("assets/character/adventurer_duck.png")
hero_slide = load_image("assets/character/adventurer_slide.png")
hero_in_pain = load_image("assets/character/adventurer_hurt.png")
hero_images = {"run": [hero_walk1, hero_walk2],
               "jump": hero_jump,
               "idle": hero_idle,
               "fall": hero_fall,
               "crouch": hero_crouch,
               "slide" : hero_slide,
               "in_pain": hero_in_pain}

block_images = {"TL": load_image("assets/tiles/top_left.png"),
                "TM": load_image("assets/tiles/top_middle.png"),
                "TR": load_image("assets/tiles/top_right.png"),
                "ER": load_image("assets/tiles/end_right.png"),
                "EL": load_image("assets/tiles/end_left.png"),
                "TP": load_image("assets/tiles/top.png"),
                "CN": load_image("assets/tiles/center.png"),
                "LF": load_image("assets/tiles/lone_float.png"),
                "SP": load_image("assets/tiles/special.png")}

coin_img = load_image("assets/items/coin.png")
speedup_img = load_image("assets/items/banana.png")
speeddown_img = load_image("assets/coins/gold_3.png")
heart_img = load_image("assets/items/bandaid.png")
oneup_img = load_image("assets/items/first_aid.png")
flag_img = load_image("assets/items/flag.png")
flagpole_img = load_image("assets/items/flagpole.png")
key_img = load_image("assets/items/genericItem_color_129.png")
chest_img = load_image("assets/items/genericItem_color_114.png")
alt_coin_img = load_image("assets/items/genericItem_color_103.png")

monster_img1 = load_image("assets/enemies/monster-1.png")
monster_img2 = load_image("assets/enemies/monster-2.png")
monster_images = [monster_img1, monster_img2]

bear_img = load_image("assets/enemies/bear-1.png")
bear_images = [bear_img]

bird_img = load_image("assets/items/genericItem_color_162.png")
bird_images = [bird_img]

sound_on_img = load_image("assets/sounds/sound_on.png")
sound_off_img = load_image("assets/sounds/sound_off.png")

# Sounds
JUMP_SOUND = pygame.mixer.Sound("assets/sounds/jump.wav")
COIN_SOUND = pygame.mixer.Sound("assets/sounds/pickup_coin.wav")
POWERUP_SOUND = pygame.mixer.Sound("assets/sounds/powerup.wav")
HURT_SOUND = pygame.mixer.Sound("assets/sounds/hurt.ogg")
DIE_SOUND = pygame.mixer.Sound("assets/sounds/death.wav")
LEVELUP_SOUND = pygame.mixer.Sound("assets/sounds/level_up.wav")
GAMEOVER_SOUND = pygame.mixer.Sound("assets/sounds/game_over.wav")

class Entity(pygame.sprite.Sprite):

    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vy = 0
        self.vx = 0

    def apply_gravity(self, level):
        self.vy += level.gravity
        self.vy = min(self.vy, level.terminal_velocity)

class Block(Entity):

    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Character(Entity):

    def __init__(self, images):
        super().__init__(0, 0, images['idle'])

        self.image_idle = images['idle']
        self.image_idle_left = pygame.transform.flip(self.image_idle, 1, 0)
        self.images_run_right = images['run']
        self.images_run_left = [pygame.transform.flip(img, 1, 0) for img in self.images_run_right]
        self.image_jump_right = images['jump']
        self.image_jump_left = pygame.transform.flip(self.image_jump_right, 1, 0)
        self.image_fall = images['fall']
        self.image_fall_left = pygame.transform.flip(self.image_fall, 1, 0)
        self.image_crouch = images['crouch']
        self.image_crouch_left = pygame.transform.flip(self.image_crouch, 1, 0)
        self.image_in_pain = images['in_pain']
        self.image_in_pain_left = pygame.transform.flip(self.image_in_pain, 1, 0)
    
        self.running_images = self.images_run_right
        self.image_index = 0
        self.steps = 0

        self.speed = 5
        self.normal_speed = 5
        self.jump_power = 20

        self.vx = 0
        self.vy = 0
        self.facing_right = True
        self.on_ground = True
        self.crouching = False
        self.has_key = False

        self.score = 0
        self.power_ups_collected = 0
        self.enemies_slain = 0
        self.collected_coins = 0
        self.total_collected_coins = 0
        self.lives = 3
        self.hearts = 3
        self.max_hearts = 3
        self.invincibility = 0
        self.powerup_time = 0

    def move_left(self):
        self.vx = -self.speed
        self.facing_right = False

    def move_right(self):
        self.vx = self.speed
        self.facing_right = True

    def crouch(self):
        if self.crouching == True and self.on_ground:
            if self.facing_right:
                self.image = self.image_crouch
                self.speed = 2
            if not self.facing_right:
                self.image = self.image_crouch_left
                self.speed = 2
        if self.crouching == False:
            self.speed = self.normal_speed
    
    def stop(self):
        self.vx = 0

    def jump(self, blocks):
        self.rect.y += 1

        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        if len(hit_list) > 0:
            self.vy = -1 * self.jump_power
            play_sound(JUMP_SOUND)

        self.rect.y -= 1

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > level.width:
            self.rect.right = level.width
        if self.rect.y > level.height and not self.on_ground:
            self.hearts = 0

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx = 0
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.vx = 0

        self.on_ground = False
        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def process_coins(self, coins):
        hit_list = pygame.sprite.spritecollide(self, coins, True)

        for coin in hit_list:
            play_sound(COIN_SOUND)
            self.score += coin.value
            self.collected_coins += 1
            self.total_collected_coins += 1
            if self.collected_coins == 10:
                self.lives += 1
                self.collected_coins = 0
    
    def process_alt_coins(self, alt_coins):
        hit_list = pygame.sprite.spritecollide(self, alt_coins, True)

        for alt_coin in hit_list:
            play_sound(COIN_SOUND)
            self.score += 200
            self.collected_coins += 1
            self.total_collected_coins += 1
            if self.collected_coins == 10:
                self.lives += 1
                self.collected_coins = 0
    


    def process_enemies(self, enemies):
        hit_list = pygame.sprite.spritecollide(self, enemies, False)

        if len(hit_list) > 0 and self.invincibility == 0 and self.vy == 0:
            play_sound(HURT_SOUND)
            self.hearts -= 1
            self.invincibility = int(0.75 * FPS)
            
        if self.on_ground == False:
            hit_list2 = pygame.sprite.spritecollide(self, enemies, True)
            for enemy in hit_list2:
                if self.vy > 0 and len(hit_list2) > 0:
                    self.score += enemy.point_value
                    self.enemies_slain += 1
                    self.vy = -15
                
    def process_powerups(self, powerups):
        hit_list = pygame.sprite.spritecollide(self, powerups, True)
        
        for p in hit_list:   
            play_sound(POWERUP_SOUND)
            self.power_ups_collected += 1
            self.score += p.value
            p.apply(self)

    def process_prizes(self, prizes):
        hit_list = pygame.sprite.spritecollide(self, prizes, True)
        
        for p in hit_list:
            self.score += p.value
            p.apply(self)

    def process_key(self, key):
        hit_list = pygame.sprite.spritecollide(self, key, True)
        
        for l in hit_list:   
            play_sound(POWERUP_SOUND)
            l.apply(self)
            
            
    def process_chest(self, chest, level):
        if self.has_key == False:
            hit_list1 = pygame.sprite.spritecollide(self, chest, False)
            for c in hit_list1:
                pass
                
                
        if self.has_key == True:
            chest.locked = False
            hit_list = pygame.sprite.spritecollide(self, chest, True)
            for c in hit_list:
                c.apply(self, level)
                self.has_key = False
        
    def check_flag(self, level):
        hit_list = pygame.sprite.spritecollide(self, level.flag, False)

        if len(hit_list) > 0:
            level.completed = True
            play_sound(LEVELUP_SOUND)
            if game.time_limit >= 330:
                self.score += 500
            if 329 >= game.time_limit >= 150:
                self.score += 250
            if 149 >= game.time_limit >= 50:
                self.score += 175
            else:
                self.score += 105
        
    def set_image(self):
        if self.on_ground:
            if self.vx != 0:
                if self.facing_right:
                    self.running_images = self.images_run_right
                else:
                    self.running_images = self.images_run_left

                self.steps = (self.steps + 1) % self.speed # Works well with 2 images, try lower number if more frames are in animation

                if self.steps == 0:
                    self.image_index = (self.image_index + 1) % len(self.running_images)
                    self.image = self.running_images[self.image_index]

            else:
                if self.facing_right:
                    self.image = self.image_idle
                else:
                    self.image = self.image_idle_left
            
        
        else:
            if self.on_ground == False and self.vy > 0:
                if self.facing_right:
                    self.image = self.image_fall
                if not self.facing_right:
                    self.image = self.image_fall_left
            
            
            elif self.facing_right:
                self.image = self.image_jump_right
            else:
                self.image = self.image_jump_left
                

    def die(self):
        self.lives -= 1
        self.speed = self.normal_speed

        if self.lives > 0:
            play_sound(DIE_SOUND)
        else:
            play_sound(GAMEOVER_SOUND)

    def respawn(self, level):
        self.rect.x = level.start_x
        self.rect.y = level.start_y
        self.hearts = self.max_hearts
        self.score = 0
        self.powerup_time = 0
        self.speed = self.normal_speed
        self.invincibility = 0
        self.has_key = False

    def update(self, level):
        self.process_enemies(level.enemies)
        self.apply_gravity(level)
        self.move_and_process_blocks(level.blocks)
        self.check_world_boundaries(level)
        self.set_image()
              
            
        if self.hearts > 0:
            self.process_coins(level.coins)
            self.process_alt_coins(level.alt_coin)
            self.process_powerups(level.powerups)
            self.process_prizes(level.prize)
            self.process_key(level.key)
            self.process_chest(level.chest, level)
            self.check_flag(level)
            self.crouch()  

            if self.invincibility > 0:
                self.invincibility -= 1
                if self.facing_right:
                    self.image = self.image_in_pain
                if not self.facing_right:
                    self.image = self.image_in_pain_left
        else:
            self.die()

class Coin(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.value = 100

class Enemy(Entity):
    def __init__(self, x, y, images):
        super().__init__(x, y, images[0])

        self.images_left = images
        self.images_right = [pygame.transform.flip(img, 1, 0) for img in images]
        self.current_images = self.images_left
        self.image_index = 0
        self.steps = 0
        
    def reverse(self):
        self.vx *= -1

        if self.vx < 0:
            self.current_images = self.images_left
        else:
            self.current_images = self.images_right

        self.image = self.current_images[self.image_index]

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
            self.reverse()
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.reverse()

    def move_and_process_blocks(self):
        pass

    def set_images(self):
        if self.steps == 0:
            self.image = self.current_images[self.image_index]
            self.image_index = (self.image_index + 1) % len(self.current_images)

        self.steps = (self.steps + 1) % 20 # Nothing significant about 20. It just seems to work okay.

    def update(self, level, hero):
        pass


    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.vx = self.start_vx
        self.vy = self.start_vy
        self.image = self.images_left[0]
        self.steps = 0

class Bear(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.start_x = x
        self.start_y = y
        self.start_vx = -2
        self.start_vy = 0

        self.vx = self.start_vx
        self.vy = self.start_vy

        self.point_value = 50

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0
                
    def is_near(self, hero):
        return abs(self.rect.x - hero.rect.x) < 2 * WIDTH

    def update(self, level, hero):
        if self.is_near(hero):
            self.apply_gravity(level)
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)
            self.set_images()

    
class Monster(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.start_x = x
        self.start_y = y
        self.start_vx = -2
        self.start_vy = 0

        self.vx = self.start_vx
        self.vy = self.start_vy

        self.point_value = 100

    def move_and_process_blocks(self, blocks):
        reverse = False

        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        reverse = True

        for block in hit_list:
            if self.vy >= 0:
                self.rect.bottom = block.rect.top
                self.vy = 0

                if self.vx > 0 and self.rect.right <= block.rect.right:
                    reverse = False

                elif self.vx < 0 and self.rect.left >= block.rect.left:
                    reverse = False
            
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0
            

        if reverse:
            self.reverse()
            
    def is_near(self, hero):
        return abs(self.rect.x - hero.rect.x) < 2 * WIDTH

    def update(self, level, hero):
        if self.is_near(hero):
            self.apply_gravity(level)
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)
            self.set_images()

    
            
class Bird(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.start_x = x
        self.start_y = y
        self.start_vx = -2
        self.start_vy = 0

        self.vx = self.start_vx
        self.vy = self.start_vy

        self.point_value = 150

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    
    def is_near_guy(self, hero):
        return abs(self.rect.x - hero.rect.x) < 2 * WIDTH

    def update(self, level, hero):
        if self.is_near_guy(hero):
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)
            self.set_images()    
    

class OneUp(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.value = 200
    def apply(self, character):
        character.lives += 1

class Prize(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.value = 200
    def apply(self, character):
        character.lives += 1


class SpeedUp(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.value = 50
    def apply(self, character):
        character.normal_speed += 2
        character.powerup_time += 10
        
class SpeedDown(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.value = -50
    def apply(self, character):
        character.normal_speed -= 2
        character.powerup_time += 10
        
class Heart(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.value = 100
    def apply(self, character):
        if character.max_hearts == 3:
            character.score += 0
        else:
            character.hearts += 1

class Flag(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Chest(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.locked = True
    def apply(self, character, level):
        if character.has_key:
            print("opened the chest")
            level.chest_opened = True
            
        if not character.has_key:
            print("ah")

class Key(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        
    def apply(self, character):
        character.has_key = True
    
class Level():

    def __init__(self, file_path):
        self.starting_blocks = []
        self.starting_enemies = []
        self.starting_coins = []
        self.starting_powerups = []
        self.starting_flag = []
        self.starting_keys = []
        self.starting_chests = []
        self.starting_prizes = []
        self.starting_alt_coins = []

        self.blocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.flag = pygame.sprite.Group()
        self.key = pygame.sprite.Group()
        self.chest = pygame.sprite.Group()
        self.prize = pygame.sprite.Group()
        self.alt_coin = pygame.sprite.Group()
        
        self.chest_opened = False

        self.active_sprites = pygame.sprite.Group()
        self.active_sprites2 = pygame.sprite.Group()
        self.inactive_sprites = pygame.sprite.Group()

        with open(file_path, 'r') as f:
            data = f.read()

        map_data = json.loads(data)

        self.width = map_data['width'] * GRID_SIZE
        self.height = map_data['height'] * GRID_SIZE
            
        self.start_x = map_data['start'][0] * GRID_SIZE
        self.start_y = map_data['start'][1] * GRID_SIZE
        self.level_name = map_data['name']
        

        for item in map_data['blocks']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            img = block_images[item[2]]
            self.starting_blocks.append(Block(x, y, img))

        for item in map_data['bears']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_enemies.append(Bear(x, y, bear_images))

        for item in map_data['monsters']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_enemies.append(Monster(x, y, monster_images))
            
        for item in map_data['birds']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_enemies.append(Bird(x, y, bird_images))

        for item in map_data['coins']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_coins.append(Coin(x, y, coin_img))

        for item in map_data['oneups']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(OneUp(x, y, oneup_img))

        for item in map_data['hearts']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(Heart(x, y, heart_img))

        for item in map_data['speedups']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(SpeedUp(x, y, speedup_img))

        for item in map_data['speeddowns']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(SpeedDown(x, y, speeddown_img))
            
        for item in map_data['keys']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_keys.append(Key(x, y, key_img))
            
        for item in map_data['chests']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_chests.append(Chest(x, y, chest_img))

        for item in map_data['prizes']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_prizes.append(Prize(x, y, oneup_img))

        for item in map_data['alt_coin']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_alt_coins.append(Coin(x, y, alt_coin_img))
            
        for i, item in enumerate(map_data['flag']):
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE

            if i == 0:
                img = flag_img
            else:
                img = flagpole_img

            self.starting_flag.append(Flag(x, y, img))
        

        self.background_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.scenery_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.inactive_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.active_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)

        if map_data['background-color'] != "":
            self.background_layer.fill(map_data['background-color'])

        if map_data['background-img'] != "":
            background_img = pygame.image.load(map_data['background-img'])

            if map_data['background-fill-y']:
                h = background_img.get_height()
                w = int(background_img.get_width() * HEIGHT / h)
                background_img = pygame.transform.scale(background_img, (w, HEIGHT))

            if "top" in map_data['background-position']:
                start_y = 0
            elif "bottom" in map_data['background-position']:
                start_y = self.height - background_img.get_height()

            if map_data['background-repeat-x']:
                for x in range(0, self.width, background_img.get_width()):
                    self.background_layer.blit(background_img, [x, start_y])
            else:
                self.background_layer.blit(background_img, [0, start_y])

        if map_data['scenery-img'] != "":
            scenery_img = pygame.image.load(map_data['scenery-img'])

            if map_data['scenery-fill-y']:
                h = scenery_img.get_height()
                w = int(scenery_img.get_width() * HEIGHT / h)
                scenery_img = pygame.transform.scale(scenery_img, (w, HEIGHT))

            if "top" in map_data['scenery-position']:
                start_y = 0
            elif "bottom" in map_data['scenery-position']:
                start_y = self.height - scenery_img.get_height()

            if map_data['scenery-repeat-x']:
                for x in range(0, self.width, scenery_img.get_width()):
                    self.scenery_layer.blit(scenery_img, [x, start_y])
            else:
                self.scenery_layer.blit(scenery_img, [0, start_y])

        pygame.mixer.music.load(map_data['music'])

        self.gravity = map_data['gravity']
        self.terminal_velocity = map_data['terminal-velocity']

        self.completed = False

        self.blocks.add(self.starting_blocks)
        self.enemies.add(self.starting_enemies)
        self.coins.add(self.starting_coins)
        self.powerups.add(self.starting_powerups)
        self.flag.add(self.starting_flag)
        self.key.add(self.starting_keys)
        self.chest.add(self.starting_chests)
        self.alt_coin.add(self.starting_alt_coins)
    
        self.prize.add(self.starting_prizes)
    
        self.active_sprites.add(self.coins, self.enemies, self.powerups, self.key, self.chest, self.alt_coin)
        self.active_sprites2.add(self.prize)
        self.inactive_sprites.add(self.blocks, self.flag)

        self.inactive_sprites.draw(self.inactive_layer)

    def reset(self, character):
        self.enemies.add(self.starting_enemies)
        self.coins.add(self.starting_coins)
        self.powerups.add(self.starting_powerups)
        self.key.add(self.starting_keys)
        self.chest.add(self.starting_chests)
        self.prize.add(self.starting_prizes)
        self.alt_coin.add(self.starting_alt_coins)
        self.chest_opened = False
        
            

        self.active_sprites.add(self.coins, self.enemies, self.powerups, self.key, self.chest, self.alt_coin)
        self.active_sprites2.add(self.prize)

        for e in self.enemies:
            e.reset()

class Game():

    SPLASH = 0
    START = 1
    PLAYING = 2
    PAUSED = 3
    LEVEL_COMPLETED = 4
    GAME_OVER = 5
    VICTORY = 6

    def __init__(self):
        self.window = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption(TITLE)
        self.done = False
        self.clock = pygame.time.Clock()
        self.refresh_rate = 60
        self.ticks = 0
        self.timer_ticks = 0
        self.time_limit = 300
        
        self.reset()

    def start(self):
        self.level = Level(levels[self.current_level])
        self.level.reset(self)
        self.level.chest_opened = False
        self.hero.respawn(self.level)
            
    def advance(self):
        self.current_level += 1
        self.hero.max_hearts += 1
        self.start()
        self.stage = Game.START

    def reset(self):
        self.hero = Character(hero_images)
        self.current_level = 0
        self.start()
        self.level.chest_opened = False
        self.stage = Game.SPLASH
        self.time_limit = 300

    def display_splash(self, surface):
        line1 = FONT_LG.render(TITLE, 1, DARK_BLUE)
        line2 = FONT_SM.render("Press any key to start.", 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;

        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;

        surface.blit(line1, (x1, y1))
        surface.blit(line2, (x2, y2))

    def display_message(self, surface, primary_text, secondary_text):
        line1 = FONT_MD.render(primary_text, 1, WHITE)
        line2 = FONT_SM.render(secondary_text, 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;

        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;

        surface.blit(line1, (x1, y1))
        surface.blit(line2, (x2, y2))

    def display_stats(self, surface):
        hearts_text = FONT_SM.render("Hearts: " + str(self.hero.hearts) + "/" + str(self.hero.max_hearts), 1, WHITE)
        lives_text = FONT_SM.render("Lives: " + str(self.hero.lives), 1, WHITE)
        score_text = FONT_SM.render("Score: " + str(self.hero.score), 1, WHITE)
        level_text = FONT_SM.render(str(self.level.level_name), 1, WHITE)
        coins_text = FONT_SM.render("Coins x" + str(self.hero.collected_coins), 1, WHITE)
        time_text = FONT_SM.render("Time left:" + str(self.time_limit), 1, WHITE)

        surface.blit(score_text, (WIDTH - score_text.get_width() - 32, 32))
        surface.blit(coins_text, (WIDTH - coins_text.get_width() - 32, 64))
        surface.blit(hearts_text, (32, 96))
        surface.blit(lives_text, (32, 128))
        surface.blit(level_text, (32, 32))
        surface.blit(time_text, (32, 64))

        if self.stage == Game.PAUSED:
            pause_text = FONT_SM.render("Paused", 1, BLACK)
            surface.blit(pause_text, (WIDTH / 2 - 46, 128))

        if self.stage == Game.PLAYING and self.hero.has_key:
            key_text = FONT_SM.render("Got the Key.", 1, WHITE)
            surface.blit(key_text, (32, 160))
        
        
        if self.stage == Game.LEVEL_COMPLETED or self.stage == Game.VICTORY:
            ending_coins_text = FONT_SM.render("Total Coins Collected: " + str(self.hero.total_collected_coins), 1, BLACK)
            ending_score_text = FONT_SM.render("Ending Score: " + str(self.hero.score), 1, BLACK)
            ending_powerup_text = FONT_SM.render("Total Powerups Collected: " + str(self.hero.power_ups_collected), 1, BLACK)
            ending_kills_text = FONT_SM.render("Total Powerups Collected: " + str(self.hero.enemies_slain), 1, BLACK)
            
            surface.blit(ending_coins_text, (32, 512))
            surface.blit(ending_score_text, (32, 544))
            surface.blit(ending_powerup_text, (32, 576))
            surface.blit(ending_kills_text, (32, 608))
    
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

            elif event.type == pygame.KEYDOWN:
                if self.stage == Game.SPLASH or self.stage == Game.START:
                    self.stage = Game.PLAYING
                    play_music()

                elif self.stage == Game.PLAYING:
                    if event.key == JUMP:
                        self.hero.jump(self.level.blocks)
                    if event.key == PAUSE:
                        self.stage = Game.PAUSED
                    if event.key == DOWN:
                        self.hero.crouching = True
                        self.hero.crouch()
            
                                  
                elif self.stage == Game.PAUSED:
                    if event.key == PAUSE:
                        self.stage = Game.PLAYING

                elif self.stage == Game.LEVEL_COMPLETED:
                    self.advance()

                elif self.stage == Game.VICTORY or self.stage == Game.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset()
                        
            elif event.type == pygame.KEYUP:
                if self.stage == Game.PLAYING and event.key == DOWN:
                    self.hero.crouching = False
                    
                        
        pressed = pygame.key.get_pressed()

        if self.stage == Game.PLAYING:   
            if pressed[LEFT]:
                self.hero.move_left()
            elif pressed[RIGHT]:
                self.hero.move_right()
            else:
                self.hero.stop()

            
        if self.hero.powerup_time != 0:
            self.ticks += 1
            if self.ticks % self.refresh_rate == 0:
                self.hero.powerup_time -= 1
                print(self.hero.powerup_time)
            if self.hero.powerup_time == 0:
                self.hero.normal_speed = 5
                
        if self.stage == Game.PLAYING and self.time_limit > 0:
            self.timer_ticks += 1
            if self.timer_ticks % self.refresh_rate == 0:
                self.time_limit -= 1
                
            if self.time_limit == 0:
                print("Times Up!")
                self.hero.hearts = 0
                self.timer_ticks = 0
                self.time_limit = 300
                
    
                
    def update(self):
        if self.stage == Game.PLAYING:
            self.hero.update(self.level)
            self.level.enemies.update(self.level, self.hero)

        if self.level.completed:
            if self.current_level < len(levels) - 1:
                self.stage = Game.LEVEL_COMPLETED
            else:
                self.stage = Game.VICTORY
            pygame.mixer.music.stop()

        elif self.hero.lives == 0:
            self.stage = Game.GAME_OVER
            pygame.mixer.music.stop()

        elif self.hero.hearts == 0:
            self.level.reset(self)
            self.hero.respawn(self.level)


    def calculate_offset(self):
        x = -1 * self.hero.rect.centerx + WIDTH / 2

        if self.hero.rect.centerx < WIDTH / 2:
            x = 0
        elif self.hero.rect.centerx > self.level.width - WIDTH / 2:
            x = -1 * self.level.width + WIDTH

        return x, 0

    def draw(self):
        offset_x, offset_y = self.calculate_offset()

        self.level.active_layer.fill(TRANSPARENT)
        self.level.active_sprites.draw(self.level.active_layer)
        

        if self.hero.invincibility % 3 < 2:
            self.level.active_layer.blit(self.hero.image, [self.hero.rect.x, self.hero.rect.y])

        if self.level.chest_opened:
            self.level.active_sprites2.draw(self.level.active_layer)

        self.window.blit(self.level.background_layer, [offset_x / 3, offset_y])
        self.window.blit(self.level.scenery_layer, [offset_x / 2, offset_y])
        self.window.blit(self.level.inactive_layer, [offset_x, offset_y])
        self.window.blit(self.level.active_layer, [offset_x, offset_y])

        self.display_stats(self.window)
        
        if self.stage == Game.SPLASH:
            self.display_splash(self.window)
        elif self.stage == Game.START:
            self.display_message(self.window, "Ready?!!!", "Press any key to start.")
        elif self.stage == Game.LEVEL_COMPLETED:
            self.display_message(self.window, "Level Complete", "Press any key to continue.")
        elif self.stage == Game.VICTORY:
            self.display_message(self.window, "You Win!", "Press 'R' to restart.")
        elif self.stage == Game.GAME_OVER:
            self.display_message(self.window, "Game Over", "Press 'R' to restart.")

            
        pygame.display.flip()

    def loop(self):
        while not self.done:
            self.process_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.start()
    game.loop()
    pygame.quit()
    sys.exit()
