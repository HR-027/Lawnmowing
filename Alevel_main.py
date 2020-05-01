import pygame
import pytmx
import sys
from os import path
from Alevel_settings import *
from Alevel_sprites import *



# Draws buttons
def draw_button(surface, text, x, y, w, h, col, action):
    mouse = pygame.mouse.get_pos()
    if ((x+w) > mouse[0] > x) and ((y+h) > mouse[1] > y):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    action()

    else:
        pygame.draw.rect(surface, col, (x, y, w, h))
        pygame.draw.rect(surface, BLACK, (x, y, w, h), 2)


    font = pygame.font.Font("KOMIKAX_.ttf", 20)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect()
    text_rect.center = ((x+(w/2)), (y+(h/2)))
    surface.blit(text_surface, text_rect)

# HUD
# Draws a health bar for the player
def draw_player_health(surface, x, y, healthlv):
    if healthlv < 0:
        healthlv = 0
    BAR_LENGTH = 200
    BAR_HEIGHT = 40
    # What percentage of the health bar is left
    fill = healthlv * BAR_LENGTH
    # The rect of the of outline and fill
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    # Changes colour depending on how much health left
    if healthlv > 0.6:
        colour = JADE
    elif healthlv > 0.3:
        colour = YELLOW
    else:
        colour = RED
    # Draws a rectangle within the outline with the size of the health left
    pygame.draw.rect(surface, colour, fill_rect)
    # Draws a rectangle outline the size of the total health
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

# Scoreboard, Pause screen
def draw_textbox(surface, text, x, y, size, colour):
    font = pygame.font.Font("KOMIKAX_.ttf", size)
    textbox_surface = font.render(text, True, colour)
    textbox_rect = textbox_surface.get_rect()
    textbox_rect.midtop = (x, y)
    surface.blit(textbox_surface, textbox_rect)

#Draws the number of lives left
def draw_lives(surface, lives, battery_img, x, y):
    for i in range(lives):
        battery_rect = battery_img.get_rect()
        battery_rect.x = x + 40 * i
        battery_rect.y = y
        surface.blit(battery_img, battery_rect)


class Game:
    def __init__(self):
        pygame.init()
        # Sets the window size
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        # sets the title
        pygame.display.set_caption(TITLE)
        # Each cycle time
        self.clock = pygame.time.Clock()
        # Calls the load file
        self.load()


    # Loads in the sprite images and the tile map
    def load(self):
        # Gets the tiled map file
        map_folder = path.dirname(__file__)
        self.map = TiledMap(path.join(map_folder, 'Alevel_tilemap.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        # Gets the lawnmower image
        self.player_img = pygame.image.load(RED_MOWER).convert_alpha()
        # Gets the wall image
        self.wall_img = pygame.image.load(WALL_TILE).convert_alpha()
        # Gets the Mole image
        self.mob_img = pygame.image.load(MOB_IMG).convert_alpha()
        # Gets the grass image
        self.grass_img = pygame.image.load(GRASS_IMG).convert_alpha()
        # The battery image
        self.battery_img = pygame.image.load(BATTERY_IMG).convert_alpha()
        # The start screen background
        self.startscreen_img = pygame.image.load(STARTSCREEN_IMG)
        # The game over background
        self.gameover_img = pygame.image.load(GAMEOVER_IMG)
        # The instructions screen
        self.instruction_img = pygame.image.load(INSTRUCT_IMG)
        self.instruction_img = pygame.transform.scale(self.instruction_img, (WIDTH, HEIGHT))

    def quit(self):
        pygame.quit()
        sys.exit()

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.grass_tiles = pygame.sprite.Group()
        # Wherever any of the following names are given in the tilemap the
        # correct sprite will be spawned there
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'Wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == 'Mole':
                Mob(self, tile_object.x, tile_object.y)
            if tile_object.name in 'grass':
                Grass_tile(self, (tile_object.x, tile_object.y))
            if tile_object.name == 'Player':
                self.player = Player(self, tile_object.x, tile_object.y)
        # Variable to check if the game is paused or not
        self.paused = False


    # Checks to see if the game is running and then calls a series of functions if it is
    def run(self):
        # Self.playing is used to check to see if the game is running
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            #  Only updates the game when not paused
            if not self.paused:
                self.update()
            self.draw()


    def update(self):
        # update the game loop
        self.all_sprites.update()

        # Check for game over
        if self.player.points == 522:
            self.winner()

        # Anytime the player collides with the grass, the grass is removed and a point is added
        hits = pygame.sprite.spritecollide(self.player, self.grass_tiles, True)
        for hit in hits:
            hit.kill()
            self.player.add_point()

        # When the player and mob collides the players health goes down
        hits = pygame.sprite.spritecollide(self.player, self.mobs, False)
        for hit in hits:
            self.player.health -= MOB_DAMAGE
            if self.player.health <= 0:
                self.player.lives -= 1
                self.player.hide()
                self.player.health = PLAYER_HEALTH
                if self.player.lives <= 0:
                    self.playing = False


    def draw(self):
        # Draws the map and sprites to the screen
        self.screen.blit(self.map_img, self.map_rect)
        self.all_sprites.draw(self.screen)
        # Draws player health
        draw_player_health(self.screen, 32, 704, self.player.health/PLAYER_HEALTH)
        # Draws Scoreboard
        pygame.draw.rect(self.screen, WHITE, pygame.Rect(912, 688, 96, 64))
        pygame.draw.rect(self.screen, BLACK, pygame.Rect(912, 688, 96, 64), 3)
        draw_textbox(self.screen, str(self.player.points), 960, 675, 50, BLACK)
        #  Draws the pause screen
        if self.paused:
            draw_textbox(self.screen, "Paused", (WIDTH/2), 288, 80, WHITE)
        # Draws how to pause
        draw_textbox(self.screen, "Hit space bar to pause", (32 * 15), 700, 30, WHITE)
        # Draws the player lives
        draw_lives(self.screen, self.player.lives, self.battery_img, WIDTH/2, HEIGHT-130)
        pygame.display.flip()


    def events(self):
        # event handler to exit the game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused


    def start_menu(self):
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

            self.screen.fill(WHITE)
            self.screen.blit(self.startscreen_img, (0, 0))

            draw_button(self.screen, "Start", 412, 150, 200, 100, WHITE, game_loop)
            draw_button(self.screen, "Instructions", 412, 350, 200, 100, WHITE, self.instruction)
            draw_button(self.screen, "Exit", 412, 550, 200, 100, WHITE, self.quit)

            pygame.display.flip()

    def instruction(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

            self.screen.fill(WHITE)
            self.screen.blit(self.instruction_img, (0, 0))
            draw_button(self.screen, "Back", (WIDTH - (32 * 7)), (HEIGHT - (32 * 5)), 200, 100, WHITE, self.start_menu)
            pygame.display.flip()
            self.clock.tick(FPS)

    def game_over(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

            self.screen.fill(BLACK)
            self.screen.blit(self.gameover_img, (0, 0))
            draw_textbox(self.screen, "Game Over", (WIDTH/2), (HEIGHT/2-(32*3)), 60, RED)
            draw_button(self.screen, "Main Menu", (32 * 3), (HEIGHT - (32 * 5)), 200, 100, WHITE, self.start_menu)
            pygame.display.flip()
            self.clock.tick(FPS)

    def winner(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
            self.screen.fill(ORANGE)
            draw_textbox(self.screen, "You won", (WIDTH/2), (HEIGHT/2-(32*3)), 60, BLACK)
            draw_button(self.screen, "Main Menu", (32 * 3), (HEIGHT - (32 * 5)), 200, 100, WHITE, self.start_menu)
            pygame.display.flip()
            self.clock.tick(FPS)


# To get the tilemap file and read it correctly
class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        # Sets the size
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        # To draw the map in the layers specified
        for layer in self.tmxdata:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pygame.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


def game_loop():
    while True:
        g.new()
        g.run()
        g.game_over()

# create the game
g = Game()
g.start_menu()
