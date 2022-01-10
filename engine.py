import os
import sys
import pygame
from PIL import Image

pygame.init()
height = 900
width = 1200
canvas = pygame.display.set_mode((width, height))
font = pygame.font.Font(None, 40)

player_hit_boxes = pygame.sprite.Group()
solids = pygame.sprite.Group()
objects = pygame.sprite.Group()
everything = pygame.sprite.Group()
groups = [player_hit_boxes, solids, objects, everything]


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"File not found: {fullname}")
        sys.exit(-1)
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Player(pygame.sprite.Sprite):
    image = load_image("cube.png")
    image2 = load_image("cube_side.png", colorkey=-1)
    image3 = pygame.transform.flip(image2, True, False)

    def __init__(self, *group, x, y):
        super().__init__(*group)
        objects.add(self)
        everything.add(self)
        self.alive = True
        self.image = Player.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.accel = complex(0, 1)
        self.speed = complex(0, 0)
        self.tp_hit_box = HitBox(player_hit_boxes, x + 7, y + 90, 76, 1)
        self.down_hit_box = HitBox(player_hit_boxes, x + 7, y + 90, 76, 1)
        self.head_hit_box = HitBox(player_hit_boxes, x + 10, y, 70, 1)
        self.hp = 100
        self.damage_cooldown = 0
        self.my_hit_boxes = pygame.sprite.Group()
        self.my_hit_boxes.add(self.tp_hit_box, self.head_hit_box, self.down_hit_box, self)

    def update(self, *args):
        self.speed += self.accel
        keys = pygame.key.get_pressed()
        for s in solids:
            if pygame.sprite.collide_rect(self.head_hit_box, s):
                self.speed = self.speed.real + 0j
                self.rect.y -= self.rect.y - s.rect.y - s.rect.h
            if pygame.sprite.collide_rect(self, s):
                self.speed = self.speed.imag * 1j + 0
                if self.rect.x - s.rect.x > 0:
                    self.rect.x += 1
                    self.speed = self.speed if self.speed.real > 0 else 0 + self.speed.imag * 1j
                else:
                    self.rect.x -= 1
                    self.speed = self.speed if self.speed.real > 0 else 0 + self.speed.imag * 1j
            if keys[pygame.K_d]:
                self.accel = self.accel.imag * 1j + 0.5
                self.image = Player.image2

            elif keys[pygame.K_a]:
                self.accel = self.accel.imag * 1j - 0.5
                self.image = Player.image3

            else:
                self.accel = self.accel.imag * 1j + 0
                self.image = Player.image

            if pygame.sprite.collide_rect(s, self.down_hit_box):
                self.speed = self.speed.real + 0j
                if pygame.key.get_pressed()[pygame.K_w]:
                    self.speed += -21j
                if pygame.sprite.collide_rect(s, self.tp_hit_box):
                    self.rect.y += s.rect.y - self.rect.y - 90
            if pygame.sprite.spritecollide(s, self.my_hit_boxes, False) and s.__class__ == Fire and self.damage_cooldown < 0:
                self.hurt(25)

        self.down_hit_box.set_pos(self.rect.x + 7, self.rect.y + 90)
        self.tp_hit_box.set_pos(self.rect.x + 7, self.rect.y + 89)
        self.head_hit_box.set_pos(self.rect.x + 10, self.rect.y)

        self.rect.x += self.speed.real
        self.rect.y += self.speed.imag
        self.speed = self.speed.real / 1.05 + self.speed.imag * 1j
        self.speed = round(self.speed.real, 3) + round(self.speed.imag, 3) * 1j
        self.damage_cooldown -= 1
        if -0.2 <= self.speed.real < 0:
            self.speed = 0 + self.speed.imag * 1j
        if self.hp <= 0:
            self.alive = False

    def debug(self):
        for i in player_hit_boxes:
            pygame.draw.rect(canvas, rect=i.rect, color="red")
        text = font.render(f"accel:{self.accel}, speed:{self.speed}, pos:{self.rect}", True, (255, 0, 0))
        canvas.blit(text, (0, 0))

    def hurt(self, hp):
        if self.damage_cooldown <= 0:
            self.hp -= hp
            self.damage_cooldown = 30

    def draw_hud(self):
        pygame.draw.rect(canvas, (255 * (1 - self.hp / 100), 255 * (self.hp / 100), 0), (25, 25, self.hp, 20))


class SolidObject(pygame.sprite.Sprite):
    image = load_image("wall.png")

    def __init__(self, *group, x, y):
        super().__init__(*group)
        everything.add(self)
        solids.add(self)
        objects.add(self)
        self.image = SolidObject.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Fire(SolidObject):
    image = load_image("fire.png", colorkey=-1)

    def __init__(self, *group, x, y):
        super().__init__(*group, x=x, y=y)
        self.image = Fire.image


class HitBox(pygame.sprite.Sprite):
    def __init__(self, group, x, y, w, h):
        super().__init__(group)
        everything.add(self)
        self.rect = pygame.rect.Rect(x, y, w, h)

    def set_pos(self, x, y):
        self.rect.x, self.rect.y = x, y


object_colors = {
    "(34, 177, 76)": SolidObject,
    "(255, 242, 0)": Player,
    "(237, 28, 36)": Fire
}


def convert_map(picture, map_file_name):
    with Image.open(os.path.join("data", picture)) as im:
        with open(os.path.join("data", map_file_name), "w+", encoding="utf8") as map_file:
            sx, sy = im.size
            pixels = im.load()
            for x in range(sx):
                for y in range(sy):
                    if str(pixels[x, y]) in object_colors.keys():
                        color = f"{pixels[x, y]}"
                        print(object_colors[color], x, y)
                        map_file.write(f"{color};{x};{y}\n")


def open_map(map_file_name):
    player = None
    for g in groups:
        g.empty()
    with open(os.path.join("data", map_file_name)) as map_file:
        for i in map_file.read().split("\n")[:-1]:
            line = i.split(";")
            print(object_colors[line[0]])
            if object_colors[line[0]] == Player:
                print("player found")
                player = object_colors[line[0]](x=int(line[1]), y=int(line[2]))
            else:
                object_colors[line[0]](x=int(line[1]), y=int(line[2]))
    return player


if __name__ == '__main__':
    convert_map("test_map1.png", "test_map1.hcm")