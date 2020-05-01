import pygame
from Alevel_settings import *
vec = pygame.math.Vector2

# For collisions between a sprite and the walls
def collide_with_walls(sprite, group, direction):
    # In the horizontal direction
    if direction == 'x':
        # Checks for hits between a sprite and the the walls
        hits = pygame.sprite.spritecollide(sprite, group, False)
        if hits:
            # When the velocity is positive then the sprite was moving to the right
            if sprite.vel.x > 0:
                # The sprite needs to be put against the left side of the wall
                sprite.pos.x = hits[0].rect.left - sprite.rect.width
            # When the velocity is negative then the sprite was moving to the left
            if sprite.vel.x < 0:
                # The sprite needs to be put against the right side of the wall
                sprite.pos.x = hits[0].rect.right + sprite.rect.width
            # To stop moving
            sprite.vel.x = 0
            sprite.rect.centerx = sprite.pos.x
    # In the vertical direction
    if direction == 'y':
        hits = pygame.sprite.spritecollide(sprite, group, False)
        if hits:
            # When the velocity is positive then the sprite was moving down
            if sprite.vel.y > 0:
                # The sprite needs to be put against the upper side of the wall
                sprite.pos.y = hits[0].rect.top - sprite.rect.height
            # When the velocity is negative then the sprite was moving up
            if sprite.vel.y < 0:
                # The sprite needs to be put against the lower side of the wall
                sprite.pos.y = hits[0].rect.bottom + sprite.rect.height
            # To stop moving
            sprite.vel.y = 0
            sprite.rect.centery = sprite.pos.y


# Player class to control things to do with the player
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        # Initialises the player class
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Gets the image of the player and sets the rect
        self.image = game.player_img
        self.rect = self.image.get_rect()
        # Velocity of the player initially zero
        self.vel = vec(0, 0)
        # Spawn in the position set
        self.pos = vec(x, y)
        # Sets the initial rotation as zero
        self.rot = 0
        # Sets the player health
        self.health = PLAYER_HEALTH
        # Sets the points to zero
        self.points = 0
        # Player lives
        self.lives = 3
        # keeps the player hidden
        self.hidden = False

    def get_keys(self):
        # Sets the velocity and rotating speed to 0 unless a key is pressed
        self.vel = vec(0, 0)
        self.rot_speed = 0
        # which key is pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pygame.K_RIGHT]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pygame.K_UP]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
        if keys[pygame.K_DOWN]:
            self.vel = vec(-PLAYER_SPEED, 0).rotate(self.rot)

    # Function to add points to the score
    def add_point(self):
        self.points += 1

    # function used to hide the player temporarily
    def hide(self):
        self.hidden = True
        self.rect.center = (WIDTH/2, HEIGHT+400)

    def update(self):
        # If the player is hidden, that ends and the player respawns at the spawn point
        if self.hidden:
            self.hidden = False
            self.rect.center = self.pos
            self.pos = vec(776, 616)

        self.get_keys()
        # Rotates according to the rotating speed and the frame rate
        # so that rotation is not instant
        self.rot = (self.rot + self.rot_speed * self.game.dt)
        # Rotates the image
        self.image = pygame.transform.rotate(self.game.player_img, self.rot)
        # Sets the position of the rect and sprite
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        # Calls for a check in collisions
        self.rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, "x")
        self.rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, "y")


class Mob(pygame.sprite.Sprite):
    # Initialises the Mob
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # Sets the image and the rect
        self.image = game.mob_img
        self.rect = self.image.get_rect()
        # Sets the position to where it was spawned
        self.pos = vec(x, y)
        # Velocity and acceleration start of at zero
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        # rect center set
        self.rect.center = self.pos
        # rotation set
        self.rot = 0

    def update(self):
        # Subtract the player vector from the mob vector to get the direction
        self.rot = (self.game.player.pos - self.pos).angle_to(vec(1, 0))
        # Rotating accordingly
        self.image = pygame.transform.rotate(self.game.mob_img, self.rot)
        # Rect created and set
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        # Acceleration set
        self.acc = vec(MOB_SPEED, 0).rotate(-self.rot)
        # Reducing the acceleration to make it less floaty
        self.acc += self.vel * -5
        self.vel += self.acc * self.game.dt
        self.pos += self.vel * self.game.dt
        # Calls the check for collisions
        self.rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')

# For any walls to spawn on the map
class Obstacle(pygame.sprite.Sprite):
    # Initialises the Obstacle class
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pygame.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

# For the grass tiles to spawn
class Grass_tile(pygame.sprite.Sprite):
    # Initialises the grass tile class
    def __init__(self, game, pos):
        self.groups = game.all_sprites, game.grass_tiles
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.grass_img
        self.rect = self.image.get_rect()
        self.rect.center = pos
