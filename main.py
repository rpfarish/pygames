import pygame
import random
import time
import os

pygame.font.init()
icon = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))
pygame.display.set_icon(icon)

Width, Height = 750, 650
Win = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Space Shooter")

# Load images
red_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
green_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
blue_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player ship
yellow_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
red_laser = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
green_laser = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
blue_laser = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
yellow_laser = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

bg = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (Width, Height))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:

    COOLDOWN = 7
    
    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(Height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter += 1


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = yellow_space_ship
        self.laser_img = yellow_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(Height):
                self.lasers.remove(laser)
            else:
                for obj in objs[:]:
                    if laser.collision(obj) and laser in self.lasers:
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, (self.ship_img.get_width() * (self.health)//self.max_health), 10))


class Enemy(Ship):
    Color_Map = {
        "red": (red_space_ship, red_laser),
        "green": (green_space_ship, green_laser),
        "blue": (blue_space_ship, blue_laser)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.Color_Map[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.color = color

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0 and self.color != "blue":
            laser = Laser(self.x - 15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
        elif self.cool_down_counter == 0:
            laser = Laser(self.x - 25, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)
    enemies = []
    wave_length = 2
    enemy_vel = level * 2 + 3
    laser_vel = 20
    player_vel = 15
    player = Player(300, 525)

    lost = False
    lost_count = 0

    def redraw_window():
        Win.blit(bg, (0, 0))
        # Draw text
        lives_label = main_font.render(f" Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f" Level: {level}", 1, (255, 255, 255))
        enemies_label = main_font.render(f" Enemies: {len(enemies)}", 1, (255, 255, 255))
        Win.blit(lives_label, (10, 10))
        Win.blit(level_label, (Width - level_label.get_width() - 10, 10))
        Win.blit(enemies_label, (10, Width - level_label.get_width() - 10))
        for enemy in enemies:
            enemy.draw(Win)

        player.draw(Win)

        if lost:
            lost_label = lost_font.render("YOU LOST!!! HAHA!!!", 1, (119, 209, 225))
            Win.blit(lost_label, (Width // 2 - lost_label.get_width() // 2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()
        keys = pygame.key.get_pressed()
        if lives <= 0 and player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        if len(enemies) == 0:
            level += 1
            level_label2 = lost_font.render(f"Level: {level}", 1, (119, 209, 225))
            Win.blit(level_label2, (Width // 2 - level_label2.get_width() // 2, 350))
            pygame.display.update()
            time.sleep(2.5)
            pygame.display.update()
            wave_length += 3
            for i in range(wave_length):
                enemy = Enemy(random.randrange(100, Width - 100), random.randrange(-1200//level, -100),
                              random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if keys[pygame.K_a] and player.x - player_vel > -5:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player.get_width() < Width:  # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player.get_height() < Height + 15:  # down
            player.y += player_vel
        if keys[pygame.K_LEFT] and player.x - player_vel > -5:  # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player.get_width() < Width:  # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player.get_height() < Height + 15:  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()
        if keys[pygame.K_r]:
            main()
        if keys[pygame.K_ESCAPE]:
            quit()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 100//(level)) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > Height:
                lives -= 1
                enemies.remove(enemy)
            if player.health == 0:
                lives -= 1
                player.health = 100


        player.move_lasers(-laser_vel, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        Win.blit(bg, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255, 255, 255))
        Win.blit(title_label, (Width // 2 - title_label.get_width() // 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()


main_menu()
