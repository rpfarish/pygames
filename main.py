import pygame
import random
import time
import os

pygame.font.init()

# Monkey
monkey_char = pygame.image.load(os.path.join("assets", "monkey.png"))
monkey_icon = pygame.image.load(os.path.join("assets", "monkey_icon.png"))
pygame.display.set_icon(monkey_icon)

# Balloon
red_balloon_img = pygame.image.load(os.path.join("assets", "red_balloon.png"))
# Arrow
arrow_img = pygame.image.load(os.path.join("assets", "arrow.png"))

# Window
Width, Height = 375, 225
Win = pygame.display.set_mode((Width, Height))
pygame.display.set_caption("Balloon Shooter v1.0")

# Background
bg = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.png")), (750 // 2, Height))


class Monkey:
    def __init__(self, x, y, img, rotation, cooldown_spd=4):
        self.x = x
        self.y = y
        self.img = img
        self.rotation = rotation
        self.cooldown_spd = cooldown_spd
        self.cool_down_counter = 0
        self.mask = pygame.mask.from_surface(self.img)
        if rotation != 0:
            self.rotate(rotation)

    def draw(self, window):
        self.cooldown()
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height, offset=50):
        return not (height - offset >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

    def rotate(self, deg):
        self.img = pygame.transform.rotate(self.img, deg)

    def cooldown(self):
        if self.cool_down_counter >= self.cooldown_spd:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1


class Balloon:
    def __init__(self, x, y, color, img, health=1):
        self.x = x
        self.y = y
        self.color = color
        self.health = health
        self.img = img
        self.mask = pygame.mask.from_surface(red_balloon_img)

    def draw(self, window):
        window.blit(red_balloon_img, (self.x, self.y))

    def off_screen(self, width):
        return not (width >= self.y >= 0)

    def off_right_screen(self, width):
        return (width <= self.x)

    def move_x(self, vel):
        self.x += vel


class Arrow:
    def __init__(self, x, y, color=1, vel=5):
        self.x = x
        self.y = y
        self.color = color
        self.arrows = []
        self.vel = vel
        self.mask = pygame.mask.from_surface(arrow_img)

    def draw(self, window):
        window.blit(arrow_img, (self.x, self.y))

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def move_y(self, vel):
        self.y += vel


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None


def main():
    run = True
    FPS = 60
    level = 1
    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)
    info_font = pygame.font.SysFont("sans", 30)
    arrows = []
    balloons = []
    wave_length = 2
    red_balloon_vel = (3 * level)
    arrow_vel = 5
    player_vel = 15
    lost = False
    balloons_num = 15
    cur_bal = 0
    timer = 0
    balloons = []
    score = 100
    info_label = info_font.render(f"Lives: {score}", 1, (255, 255, 255))

    for i in range(balloons_num):
        ran = random.randrange(Width * -4, -50)

        balloons.append(Balloon(ran - 600, 100, red_balloon_img, "red"))

    monkey = Monkey(Width // 3 + 25, 5, monkey_char, 180)

    # TODO move darts to monkey class
    def redraw_window():
        Win.blit(bg, (0, 0))
        # Win.fill((0, 0, 0))

        Win.blit(info_label, (
            Width // 2 - info_label.get_width() // 2 - 120,
            Height // 2 - info_label.get_height() // 2 - 95))

        # Draw everything here if it happens during the game
        # for balloon in balloons:
        #     balloon.draw(Win)
        monkey.draw(Win)

        for balloon in balloons:
            balloon.draw(Win)
        for arrow in arrows:
            arrow.draw(Win)
        if lost:
            quit()
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pos()
        # print(mouse)
        for i in balloons:
            i.move_x(1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        if keys[pygame.K_ESCAPE]:
            quit()

        if timer >= 150:
            arrows.append(Arrow(150, 15))
            timer = 0

        for arrow in range(len(arrows)):
            ar = arrows[arrow]
            ar.move_y(2)

        for balloon in balloons:
            if balloon.off_right_screen(375):
                score -= 1
                info_label = info_font.render(f"Lives: {score}", 1, (255, 255, 255))
                balloons.remove(balloon)

        for balloon in balloons:
            for arrow in range(len(arrows)):

                if collide(balloon, arrows[arrow]):
                    arrows.remove(arrows[arrow])
                    balloons.remove(balloon)
        for arrow in range(len(arrows)):
            # print(arrow)
            if len(arrows) > arrow:
                if arrows[arrow].off_screen(Height):
                    arrows.remove(arrows[arrow])

        # print(arrows)
        timer += 1


if __name__ == '__main__':
    main()
