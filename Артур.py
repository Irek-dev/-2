import pygame
import cv2
import random
import os
import sys
import sqlite3

db = sqlite3.connect('users.db')
sql = db.cursor()
a = input('Введите имя: ')
b = input('Введите фамилию: ')
c = int(input('Введите возраст: '))
sql.execute('''CREATE TABLE IF NOT EXISTS users (
                        name TEXT,
                        surname TEXT,
                        age BIGINT
                    )''')
sql.execute(f"SELECT name From users WHERE name = '{a}'")
if sql.fetchone() is None:
    sql.execute(f"INSERT INTO users VALUES (?, ?, ?)", (a, b, c))
    db.commit()
else:
    print('Вы уже есть в базе данных')
db.commit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image
    image = pygame.image.load(fullname)
    return image


class Plitka(pygame.sprite.Sprite):
    def __init__(self, filename, x, y):
        super().__init__()

        self.name = filename.split('.')[0]

        self.image_nam = pygame.image.load('готовые иконки/' + filename)

        self.back_image = pygame.image.load('готовые иконки/' + filename)
        pygame.draw.rect(self.back_image, white, self.back_image.get_rect())

        self.image = self.back_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.view = False

    def update(self):
        self.image = self.image_nam if self.view else self.back_image

    def show(self):
        self.view = True

    def hide(self):
        self.view = False


class Game():
    def __init__(self):
        self.level = 1
        self.level_com = False

        self.all_picture = [f for f in os.listdir('готовые иконки') if os.path.join('готовые иконки', f)]

        self.img_width, self.img_heigth = (128, 128)
        self.padding = 20
        self.margin_top = 160
        self.cols = 4
        self.rows = 2
        self.width = 1280

        self.plitkas_group = pygame.sprite.Group()

        self.flipped = []
        self.frame_count = 0
        self.block_game = False

        self.generate_level(self.level)

        self.video_playing = True
        self.video_on = pygame.image.load('картинки/on.png').convert_alpha()
        self.video_off = pygame.image.load('картинки/off.png').convert_alpha()
        self.video_control = self.video_on
        self.video_control_rect = self.video_control.get_rect(topright=(WIDTH - 50, 10))
        self.make_video()

        self.music_playing = True
        self.sound_on = pygame.image.load('картинки/play.png').convert_alpha()
        self.sound_off = pygame.image.load('картинки/pause.png').convert_alpha()
        self.music_control = self.sound_on
        self.music_control_rect = self.music_control.get_rect(topright=(WIDTH - 10, 10))

        pygame.mixer.music.load('музыка/the-future-bass-15017.mp3')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play()

    def update(self, event_list):
        if self.video_playing:
            self.succes, self.img = self.video.read()
        self.press_button(event_list)
        self.draw()
        self.check_level_complete(event_list)

    def check_level_complete(self, event_list):
        if not self.block_game:
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for j in self.plitkas_group:
                        if j.rect.collidepoint(event.pos):
                            self.flipped.append(j.name)
                            j.show()
                            if len(self.flipped) == 2:
                                if self.flipped[0] != self.flipped[1]:
                                    self.block_game = True
                                else:
                                    self.flipped = []
                                    for j in self.plitkas_group:
                                        if j.view:
                                            self.level_com = True
                                        else:
                                            self.level_com = False
                                            break
        else:
            self.frame_count += 1
            if self.frame_count == fps:
                self.frame_count = 0
                self.block_game = False

                for i in self.plitkas_group:
                    if i.name in self.flipped:
                        i.hide()
                self.flipped = []

    def do(self, tech):
        self.cols = self.rows = self.cols if self.cols >= self.rows else self.rows

        plitkas_width = (self.img_width * self.cols + self.padding * 3)
        left_pole = right_pole = (self.width - plitkas_width) // 2
        tiles = []
        self.plitkas_group.empty()

        for i in range(len(tech)):
            x = left_pole + ((self.img_width + self.padding) * (i % self.cols))
            y = self.margin_top + (i // self.rows * (self.img_heigth + self.padding))
            plitka = Plitka(tech[i], x, y)
            self.plitkas_group.add(plitka)

    def generate_level(self, level):
        self.program = self.select_ramdom(self.level)
        self.level_com = False
        self.rows = self.level + 1
        self.cols = 4
        self.do(self.program)

    def select_ramdom(self, level):
        tech = random.sample(self.all_picture, (self.level + self.level + 2))
        tech_copy = tech.copy()
        tech.extend(tech_copy)
        random.shuffle(tech)
        return tech

    def press_button(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.music_control_rect.collidepoint(pygame.mouse.get_pos()):
                    if self.music_playing:
                        self.music_playing = False
                        self.music_control = self.sound_off
                        pygame.mixer.music.pause()

                    else:
                        self.music_playing = True
                        self.music_control = self.sound_on
                        pygame.mixer.music.unpause()
                if self.video_control_rect.collidepoint(pygame.mouse.get_pos()):
                    if self.video_playing:
                        self.video_playing = False
                        self.video_control = self.video_off
                    else:
                        self.video_playing = True
                        self.video_control = self.video_on
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.level_com:
                    self.level += 1
                    if self.level >= 4:
                        self.level = 1
                    self.generate_level(self.level)

    def draw(self):
        screen.fill(black)

        # шрифты
        tit_font = pygame.font.Font('pygame шрифт/шрифт pygame.ttf', 44)
        con_font = pygame.font.Font('pygame шрифт/шрифт pygame.ttf', 30)

        # text
        tit_text = tit_font.render('Игра на память.', True, white)
        tit_rect = tit_text.get_rect(midtop=(WIDTH // 2 - 350, 10))

        lvl_text = con_font.render('Уровень ' + str(self.level), True, white)
        lvl_rect = lvl_text.get_rect(midtop=(WIDTH // 2, 100))

        inf_text = tit_font.render('Найди 2 одинаковые картинки.', True, white)
        inf_rect = inf_text.get_rect(midtop=(WIDTH // 2 + 150, 10))

        if self.video_playing:
            if self.succes:
                screen.blit(pygame.image.frombuffer(self.img.tobytes(), self.shape, 'BGR'), (0, 50))
            else:
                self.make_video()
        else:
            screen.blit(pygame.image.frombuffer(self.img.tobytes(), self.shape, 'BGR'), (0, 50))
        if self.level != 3:
            next_lvl_text = con_font.render('Вы прошли уровень! Нажмите пробел, чтобы перейти на следующий уровень',
                                            True, white)
        else:
            next_lvl_text = con_font.render('Победа!', True, white)
        next_lvl_rect = next_lvl_text.get_rect(midbottom=(WIDTH // 2, HEIGHT - 40))

        pygame.draw.rect(screen, red, (WIDTH - 90, 0, 100, 50))
        screen.blit(self.music_control, self.music_control_rect)
        screen.blit(self.video_control, self.video_control_rect)

        screen.blit(tit_text, tit_rect)
        screen.blit(lvl_text, lvl_rect)
        screen.blit(inf_text, inf_rect)

        self.plitkas_group.draw(screen)
        self.plitkas_group.update()

        if self.level_com:
            screen.blit(next_lvl_text, next_lvl_rect)

    def make_video(self):
        self.video = cv2.VideoCapture('видео/Matrix - 47802.mp4')
        self.succes, self.img = self.video.read()
        self.shape = self.img.shape[1::-1]


pygame.init()

white = (255, 255, 255)
red = (255, 0, 0)
black = (0, 0, 0)
WIDTH = 1280
HEIGHT = 860
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Тренировка памяти')

fps = 60
clock = pygame.time.Clock()

game = Game()

run = True
while run:
    game_list = pygame.event.get()
    for event in game_list:
        if event.type == pygame.QUIT:
            run = False

    game.update(game_list)

    pygame.display.update()
    clock.tick(fps)

pygame.quit()
