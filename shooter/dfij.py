from pygame import *
from random import randint
from time import time as timer

# Ініціалізація шрифтів і текстів
font.init()
font1 = font.Font(None, 80)
win_text = font1.render('YOU WIN', True, (255, 255, 255))
lose_text = font1.render('YOU LOSE', True, (180, 0, 0))
font2 = font.Font(None, 36)

# Ініціалізація музики
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play(-1)
fire_sound = mixer.Sound('fire.ogg')

# Зображення
img_back = 'galaxy.jpg'
img_hero = 'rocket.png'
img_bullet = 'bullet.png'
img_enemy = 'ufo.png'
img_ast = 'asteroid.png'
img_bust = 'upgrade.png'
img_upgrade = 'upgradee.png'
img_fon = 'menu_fonn.jpeg'  # Використовуємо JPEG для меню
new_rocket = 'new_rocket.png'

# Початкові значення
score = 0
goal = 10
lost = 0
max_lost = 3
life = 3

# Клас для спрайтів
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# Клас гравця
class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.speed_original = player_speed
        self.speed_boosted = player_speed * 2
        self.boost_time = 0
        self.boost_duration = 5
        self.shield = False
        self.shield_time = 0
        self.shield_duration = 5
        self.asteroid_busting_time = 0
        self.asteroid_busting_duration = 10
        self.asteroid_busting_enabled = False
        self.hit_counter = 0  # Лічильник зіткнень

    def update(self):
        # Відключення бустів за часом
        if self.shield and timer() - self.shield_time >= self.shield_duration:
            self.shield = False
        if self.boost_time > 0 and timer() - self.boost_time >= self.boost_duration:
            self.speed = self.speed_original
            self.boost_time = 0
        if self.asteroid_busting_time > 0 and timer() - self.asteroid_busting_time >= self.asteroid_busting_duration:
            self.asteroid_busting_enabled = False
            self.asteroid_busting_time = 0

        # Рух гравця
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

    def activate_boost(self):
        self.speed = self.speed_boosted
        self.boost_time = timer()

    def activate_asteroid_busting(self):
        if not self.asteroid_busting_enabled:
            self.asteroid_busting_enabled = True
            self.asteroid_busting_time = timer()

    def activate_shield(self):
        self.shield = True
        self.shield_time = timer()

    def add_asteroid_busting_upgrade(self):
        self.asteroid_busting_enabled = True
        self.asteroid_busting_time = timer()

# Клас ворогів (використовується також для астероїдів і бустів)
class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost += 1

# Клас для спрайту апгрейдів (якщо хочете використовувати окремий клас)
class Upgrade(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0

# Клас кулі
class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()

# Клас для просунутих ворогів
class AdvancedEnemy(Enemy):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.direction = 1

    def update(self):
        if self.direction == 1:
            self.rect.x += self.speed
            if self.rect.x > win_width - self.rect.width:
                self.direction = -1
        else:
            self.rect.x -= self.speed
            if self.rect.x < 0:
                self.direction = 1
        self.rect.y += self.speed
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0

# Ініціалізація вікна
win_width = 700
win_height = 500
display.set_caption('Shooter')
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load(img_back), (win_width, win_height))

# Створення гравця
ship = Player(img_hero, 5, win_height - 100, 80, 100, 10)

# Створення груп ворогів, астероїдів, апгрейдів і кулі
monsters = sprite.Group()
for i in range(1, 4):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(2, 5))
    monsters.add(monster)

advanced_enemies = sprite.Group()
for i in range(1, 3):
    adv_enemy = AdvancedEnemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(2, 5))
    advanced_enemies.add(adv_enemy)

asteroids = sprite.Group()
for i in range(1, 3):
    asteroid = Enemy(img_ast, randint(30, win_width - 30), -40, 70, 50, randint(1, 7))
    asteroids.add(asteroid)

upgrades = sprite.Group()
for i in range(1, 3):
    upg = Enemy(img_bust, randint(30, win_width - 30), -40, 70, 50, randint(1, 5))
    upgrades.add(upg)

upgrades2 = sprite.Group()
for i in range(1, 3):
    upg2 = Enemy(img_upgrade, randint(30, win_width - 30), -40, 70, 50, randint(1, 5))
    upgrades2.add(upg2)

bullets = sprite.Group()

# Функція для меню
def show_menu():
    menu_font = font.Font(None, 100)
    play_text = menu_font.render('Play', True, (255, 255, 255))
    play_rect = play_text.get_rect(center=(win_width // 2, win_height // 2))
    menu_background = transform.scale(image.load(img_fon), (win_width, win_height))
    window.blit(menu_background, (0, 0))
    window.blit(play_text, play_rect)
    display.update()

    waiting_for_input = True
    while waiting_for_input:
        for e in event.get():
            if e.type == QUIT:
                return False
            elif e.type == MOUSEBUTTONDOWN:
                if play_rect.collidepoint(e.pos):
                    return "play"
    return False

# Змінні для таймерів спавну астероїдів і апгрейдів
spawn_interval_asteroid = 3   # Інтервал для астероїдів (секунд)
spawn_interval_upgrade = 7    # Інтервал для бустів (секунд)
last_asteroid_spawn = timer()
last_upgrade_spawn = timer()

# Основні змінні гри
finish = False
run = True
rel_time = False
num_fire = 0

# Показуємо меню перед початком гри
if not show_menu():
    run = False

menu_result = show_menu()
if menu_result == "play":
    pass  # Можна додатково реалізувати логіку меню

clock = time.Clock()

while run:
    clock.tick(20)  # Обмеження до 60 FPS

    # Обробка подій
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                if num_fire < 5 and not rel_time:
                    num_fire += 1
                    fire_sound.play()
                    ship.fire()
                if num_fire >= 5 and not rel_time:
                    last_time = timer()
                    rel_time = True

    if not finish:
        window.blit(background, (0, 0))

        # Спавн астероїдів через заданий інтервал
        if timer() - last_asteroid_spawn > spawn_interval_asteroid:
            new_asteroid = Enemy(img_ast, randint(30, win_width - 30), -40, 70, 50, randint(1, 7))
            asteroids.add(new_asteroid)
            last_asteroid_spawn = timer()

        # Спавн бустів через заданий інтервал
        if timer() - last_upgrade_spawn > spawn_interval_upgrade:
            upgrade_type = randint(1, 2)
            if upgrade_type == 1:
                new_upgrade = Enemy(img_bust, randint(30, win_width - 30), -40, 70, 50, randint(2, 4))
                upgrades.add(new_upgrade)
            else:
                new_upgrade2 = Enemy(img_upgrade, randint(30, win_width - 30), -40, 70, 50, randint(2, 4))
                upgrades2.add(new_upgrade2)
            last_upgrade_spawn = timer()

        # Оновлення спрайтів
        ship.update()
        monsters.update()
        advanced_enemies.update()
        bullets.update()
        asteroids.update()
        upgrades.update()
        upgrades2.update()

        # Відображення спрайтів
        ship.reset()
        monsters.draw(window)
        advanced_enemies.draw(window)
        asteroids.draw(window)
        bullets.draw(window)
        upgrades.draw(window)
        upgrades2.draw(window)

        # Обмеження пострілів
        if rel_time:
            now_time = timer()
            if now_time - last_time < 3:
                reload_text = font2.render('Wait, reload...', 1, (150, 0, 0))
                window.blit(reload_text, (260, 460))
            else:
                num_fire = 0
                rel_time = False

        # Перевірка зіткнень: кулі - вороги
        collisions = sprite.groupcollide(monsters, bullets, True, True)
        for c in collisions:
            score += 1
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        # Якщо пропущено забагато ворогів
        if lost >= 20:
            finish = True
            window.blit(lose_text, (200, 200))

        # Перевірка зіткнень: гравець - вороги
        collisions_with_monsters = sprite.spritecollide(ship, monsters, True)
        for monster in collisions_with_monsters:
            if not ship.shield:
                life -= 1
            if life == 0 or lost >= max_lost:
                finish = True
                window.blit(lose_text, (200, 200))

        # Перевірка зіткнень: гравець - астероїди
        collisions_with_asteroids = sprite.spritecollide(ship, asteroids, True)
        for asteroid in collisions_with_asteroids:
            life -= 1
            new_asteroid = Enemy(img_ast, randint(80, win_width - 80), -40, 80, 50, randint(2, 5))
            asteroids.add(new_asteroid)
            if life == 0 or lost >= max_lost:
                finish = True
                window.blit(lose_text, (200, 200))

        # Перевірка зіткнень: кулі - просунуті вороги
        collisions_advanced = sprite.groupcollide(advanced_enemies, bullets, True, True)
        for c in collisions_advanced:
            score += 2
            adv_enemy = AdvancedEnemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(2, 5))
            advanced_enemies.add(adv_enemy)

        # Перевірка зіткнень: гравець - просунуті вороги
        collisions_with_advanced = sprite.spritecollide(ship, advanced_enemies, False)
        for adv_enemy in collisions_with_advanced:
            life -= 1
            adv_enemy.rect.x = randint(80, win_width - 80)
            adv_enemy.rect.y = -40
            if life == 0 or lost >= max_lost:
                finish = True
                window.blit(lose_text, (200, 200))

        # Перевірка зіткнень: гравець - бусти
        if sprite.spritecollide(ship, upgrades, True):
            ship.activate_boost()
        if sprite.spritecollide(ship, upgrades2, True):
            ship.add_asteroid_busting_upgrade()

        # Якщо активовано "asteroid busting", кулі руйнують астероїди
        if ship.asteroid_busting_enabled:
            collisions = sprite.groupcollide(asteroids, bullets, True, True)
            for c in collisions:
                score += 1

        # Перевірка на досягнення цілі
        if score >= goal:
            finish = True
            window.blit(win_text, (200, 200))

        # Виведення рахунку та кількості пропущених ворогів
        score_disp = font2.render("Рахунок: " + str(score), 1, (255, 255, 255))
        window.blit(score_disp, (10, 20))
        lost_disp = font2.render("Пропущено: " + str(lost), 1, (255, 255, 255))
        window.blit(lost_disp, (10, 50))

        # Виведення інформації про активні бусти
        boosts_text = ""
        if ship.boost_time > 0 and timer() - ship.boost_time < ship.boost_duration:
            remaining_boost = ship.boost_duration - (timer() - ship.boost_time)
            boosts_text += f"Speed boost {int(remaining_boost)}s left\n"
        if ship.shield and timer() - ship.shield_time < ship.shield_duration:
            remaining_shield = ship.shield_duration - (timer() - ship.shield_time)
            boosts_text += f"Shield: {int(remaining_shield)}s left\n"
        if ship.asteroid_busting_enabled and ship.asteroid_busting_time > 0 and timer() - ship.asteroid_busting_time < ship.asteroid_busting_duration:
            remaining_destroy = ship.asteroid_busting_duration - (timer() - ship.asteroid_busting_time)
            boosts_text += f"Destroy boost: {int(remaining_destroy)}s left\n"
        boosts_disp = font2.render(boosts_text, 1, (255, 255, 255))
        window.blit(boosts_disp, (10, 80))

        # Виведення залишків життя
        life_color = (0, 150, 0) if life == 3 else (150, 150, 0) if life == 2 else (150, 0, 0)
        life_disp = font1.render(str(life), 1, life_color)
        window.blit(life_disp, (650, 10))

        display.update()

    else:
        # Скидання гри після завершення
        finish = False
        score = 0
        lost = 0
        num_fire = 0
        life = 3

        for group in [advanced_enemies, bullets, monsters, asteroids, upgrades, upgrades2]:
            group.empty()

        # Відновлення початкових ворогів, астероїдів і бустів
        for i in range(1, 4):
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(2, 5))
            monsters.add(monster)
        for i in range(1, 3):
            asteroid = Enemy(img_ast, randint(30, win_width - 30), -40, 70, 50, randint(1, 7))
            asteroids.add(asteroid)
        for i in range(1, 3):
            upg = Enemy(img_bust, randint(30, win_width - 30), -40, 70, 50, randint(2, 4))
            upgrades.add(upg)
        for i in range(1, 3):
            upg2 = Enemy(img_upgrade, randint(30, win_width - 30), -40, 70, 50, randint(2, 4))
            upgrades2.add(upg2)

        time.delay(3000)

# Завершення роботи
quit()
