from pygame import *


class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y):
        sprite.Sprite.__init__(self)
        self.image_normal = transform.scale(image.load(player_image), (size_x, size_y))
        self.image = self.image_normal
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def update(self, mouse_pos, player_image_hover, size_x, size_y):
        if self.rect.collidepoint(mouse_pos):
            self.image_hover = transform.scale(image.load(player_image_hover), (size_x, size_y))
            self.image = self.image_hover
        else:
            self.image = self.image_normal

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_x_speed, player_y_speed):
        GameSprite.__init__(self, player_image, player_x, player_y, size_x, size_y)
        self.x_speed = player_x_speed
        self.y_speed = player_y_speed
        self.on_ground = False
        self.gravity = 1
        self.jump_power = -17
        self.direction = "right"
        self.active_skin = "Harry"
        self.double_jump = False
        self.high_jump = False
        self.fast_move = False
        self.shield = False
        self.multi_bullet = False
        self.jump_counter = 0

        self.skin_images = {
            "Harry": transform.scale(image.load("images/Harry.png"), (size_x, size_y)),
            "Hermiona": transform.scale(image.load("images/Hermiona.png"), (size_x, size_y)),
            "Ron": transform.scale(image.load("images/Ron.png"), (size_x, size_y)),
            "Damboldor": transform.scale(image.load("images/Damboldor.png"), (size_x, size_y)),
            "Profesor": transform.scale(image.load("images/Profesor.png"), (size_x, size_y))
        }

        self.image_normal = self.skin_images[self.active_skin]
        self.image = self.image_normal

    def apply_skin(self, skin_name):
        if skin_name in self.skin_images:
            self.active_skin = skin_name
            self.image_normal = self.skin_images[skin_name]
            self.image = self.image_normal
            return True
        return False

    def update(self, barriers, platforms):
        move_speed = self.x_speed
        if self.fast_move:
            move_speed = self.x_speed * 1.5

        if self.rect.x <= win_width - 80 and move_speed > 0 or self.rect.x >= 0 and move_speed < 0:
            self.rect.x += move_speed

        platforms_touched = sprite.spritecollide(self, barriers, False)
        if move_speed > 0:
            for p in platforms_touched:
                self.rect.right = min(self.rect.right, p.rect.left)
        elif move_speed < 0:
            for p in platforms_touched:
                self.rect.left = max(self.rect.left, p.rect.right)

        if move_speed > 0:
            self.direction = "right"
        elif move_speed < 0:
            self.direction = "left"

        if not self.on_ground:
            self.y_speed += self.gravity

        self.rect.y += self.y_speed

        self.on_ground = False

        platforms_touched = sprite.spritecollide(self, platforms, False)
        if self.y_speed > 0:
            for p in platforms_touched:
                self.on_ground = True
                self.rect.bottom = min(self.rect.bottom, p.rect.top)
                self.y_speed = 0
                self.jump_counter = 0
        elif self.y_speed < 1:
            for p in platforms_touched:
                self.rect.top = max(self.rect.top, p.rect.bottom)
                self.y_speed = 0

        walls_touched = sprite.spritecollide(self, barriers, False)
        if self.y_speed > 0:
            for wall in walls_touched:
                if wall.rect.width > 30:
                    if abs(self.rect.bottom - wall.rect.top) < 10:
                        self.on_ground = True
                        self.rect.bottom = wall.rect.top
                        self.y_speed = 0
                        self.jump_counter = 0

        if self.rect.top > win_height:
            return True
        return False

    def jump(self):
        if self.on_ground:
            jump_power = self.jump_power
            if self.high_jump:
                jump_power = self.jump_power * 1.3
            self.y_speed = jump_power
            self.jump_counter = 1
        elif self.double_jump and self.jump_counter == 1:
            jump_power = self.jump_power
            if self.high_jump:
                jump_power = self.jump_power * 1.3
            self.y_speed = jump_power
            self.jump_counter = 2

    def fire(self):
        global bullets
        if self.multi_bullet:
            if self.direction == "right":
                bullet1 = Bullet('images/bullet.png', self.rect.right, self.rect.centery, 15, 10, 15)
                bullet2 = Bullet('images/bullet.png', self.rect.right, self.rect.centery - 20, 15, 10, 15)
                bullet3 = Bullet('images/bullet.png', self.rect.right, self.rect.centery + 20, 15, 10, 15)
            else:
                bullet1 = Bullet('images/bullet.png', self.rect.left - 15, self.rect.centery, 15, 10, -15)
                bullet2 = Bullet('images/bullet.png', self.rect.left - 15, self.rect.centery - 20, 15, 10, -15)
                bullet3 = Bullet('images/bullet.png', self.rect.left - 15, self.rect.centery + 20, 15, 10, -15)
            bullets.add(bullet1)
            bullets.add(bullet2)
            bullets.add(bullet3)
        else:
            # Обычная стрельба
            if self.direction == "right":
                bullet = Bullet('images/bullet.png', self.rect.right, self.rect.centery, 15, 10, 15)
            else:
                bullet = Bullet('images/bullet.png', self.rect.left - 15, self.rect.centery, 15, 10, -15)
            bullets.add(bullet)


class Enemy_h(GameSprite):
    side = "left"

    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed, x1, x2):
        GameSprite.__init__(self, player_image, player_x, player_y, size_x, size_y)
        self.speed = player_speed
        self.x1 = x1
        self.x2 = x2

    def update(self):
        if self.rect.x <= self.x1:
            self.side = "right"
        if self.rect.x >= self.x2:
            self.side = "left"
        if self.side == "left":
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed


class Enemy_v(GameSprite):
    side = "up"

    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed, y1, y2):
        GameSprite.__init__(self, player_image, player_x, player_y, size_x, size_y)
        self.speed = player_speed
        self.y1 = y1
        self.y2 = y2

    def update(self):
        if self.rect.y <= self.y1:
            self.side = "down"
        if self.rect.y >= self.y2:
            self.side = "up"
        if self.side == "up":
            self.rect.y -= self.speed
        else:
            self.rect.y += self.speed


class Bullet(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        GameSprite.__init__(self, player_image, player_x, player_y, size_x, size_y)
        self.speed = player_speed

    def update(self):
        self.rect.x += self.speed
        if self.rect.x > win_width + 10 or self.rect.x < -10:
            self.kill()


class ShopItem:
    def __init__(self, name, description, price, image_path, type_item="boost", unlocked=False):
        self.name = name
        self.description = description
        self.price = price
        self.image_path = image_path
        self.type = type_item
        self.unlocked = unlocked
        self.active = False


def create_level(level_name):
    global barriers, platforms, monsters, coins, bullets, boss_bullets, boss, active_skin

    barriers.empty()
    platforms.empty()
    monsters.empty()
    coins.empty()
    bullets.empty()

    if 'boss_bullets' not in globals():
        global boss_bullets
        boss_bullets = sprite.Group()
    else:
        boss_bullets.empty()

    hero = None
    final_sprite = None
    boss = None

    hero_x, hero_y, hero_size_x, hero_size_y = 50, 570, 80, 80

    if level_name == "lvl1":
        floor = GameSprite('images/wall2.png', 0, 650, 1200, 50)
        platforms.add(floor)

        platforms.add(GameSprite('images/platform.png', 300, 550, 250, 30))
        platforms.add(GameSprite('images/platform.png', 700, 500, 250, 30))

        for i in range(2):
            for j in range(2):
                coins.add(GameSprite('images/coin.png', 150 + i * 50, 500 + j * 50, 40, 40))

        for i in range(4):
            for j in range(2):
                coins.add(GameSprite('images/coin.png', 750 + i * 50, 350 + j * 50, 40, 40))

        monsters.add(Enemy_h('images/enemy.png', 350, 520, 80, 80, 2, 320, 480))
        monsters.add(Enemy_h('images/enemy.png', 750, 470, 80, 80, 2, 720, 880))

        hero = Player('images/Harry.png', hero_x, hero_y, hero_size_x, hero_size_y, 0, 0)
        final_sprite = GameSprite('images/door.png', 1050, 550, 100, 100)

    elif level_name == "lvl2":
        floor_left = GameSprite('images/wall2.png', 0, 650, 350, 50)
        floor_right = GameSprite('images/wall2.png', 850, 650, 350, 50)
        platforms.add(floor_left)
        platforms.add(floor_right)

        platforms.add(GameSprite('images/platform.png', 300, 550, 180, 30))
        platforms.add(GameSprite('images/platform.png', 550, 500, 180, 30))
        platforms.add(GameSprite('images/platform.png', 800, 550, 180, 30))

        for i in range(5):
            coins.add(GameSprite('images/coin.png', 620, 250 + i * 50, 40, 40))

        for i in range(5):
            if i != 2:
                coins.add(GameSprite('images/coin.png', 450 + i * 70, 350, 40, 40))

        coins.add(GameSprite('images/coin.png', 620, 350, 50, 50))

        monsters.add(Enemy_h('images/enemy.png', 400, 520, 80, 80, 3, 330, 470))
        monsters.add(Enemy_h('images/enemy.png', 700, 470, 80, 80, 3, 580, 770))

        hero = Player('images/Harry.png', hero_x, hero_y, hero_size_x, hero_size_y, 0, 0)
        final_sprite = GameSprite('images/door.png', 1050, 550, 100, 100)

    elif level_name == "lvl3":
        floor = GameSprite('images/wall2.png', 0, 650, 500, 50)
        platforms.add(floor)

        platforms.add(GameSprite('images/platform.png', 450, 525, 350, 30))
        platforms.add(GameSprite('images/platform.png', 850, 400, 350, 30))
        platforms.add(GameSprite('images/platform.png', 200, 400, 250, 30))
        platforms.add(GameSprite('images/platform.png', 500, 250, 250, 30))

        for i in range(6):
            coins.add(GameSprite('images/coin.png', 250 + i * 40, 220, 40, 40))

        for i in range(2):
            for j in range(2):
                coins.add(GameSprite('images/coin.png', 550 + i * 50, 120 + j * 50, 40, 40))

        for i in range(3):
            coins.add(GameSprite('images/coin.png', 150, 550 + i * 30, 40, 40))

        monsters.add(Enemy_h('images/enemy.png', 500, 395, 80, 80, 2, 450, 700))
        monsters.add(Enemy_h('images/enemy.png', 900, 370, 80, 80, 2, 850, 1100))

        hero = Player('images/Harry.png', hero_x, hero_y, hero_size_x, hero_size_y, 0, 0)
        final_sprite = GameSprite('images/door.png', 1050, 300, 100, 100)

    elif level_name == "lvl4":
        platforms.add(GameSprite('images/wall2.png', 0, 650, 350, 50))
        platforms.add(GameSprite('images/wall2.png', 420, 650, 350, 50))
        platforms.add(GameSprite('images/wall2.png', 850, 250, 50, 50))

        platforms.add(GameSprite('images/platform.png', 100, 550, 180, 30))
        platforms.add(GameSprite('images/platform.png', 350, 500, 180, 30))
        platforms.add(GameSprite('images/platform.png', 600, 450, 180, 30))
        platforms.add(GameSprite('images/platform.png', 850, 400, 180, 30))
        platforms.add(GameSprite('images/platform.png', 1100, 350, 180, 30))

        platforms.add(GameSprite('images/platform.png', 200, 300, 120, 30))
        platforms.add(GameSprite('images/platform.png', 400, 250, 120, 30))
        platforms.add(GameSprite('images/platform.png', 600, 200, 120, 30))

        for i in range(3):
            coins.add(GameSprite('images/coin.png', 550 + i * 40, 100, 40, 40))
        for i in range(3):
            coins.add(GameSprite('images/coin.png', 510 - i * 30, 100 + i * 30, 40, 40))
        for i in range(3):
            coins.add(GameSprite('images/coin.png', 670 + i * 30, 100 + i * 30, 40, 40))

        for i in range(4):
            coins.add(GameSprite('images/coin.png', 350 + i * 40, 380, 40, 40))
        for i in range(2):
            coins.add(GameSprite('images/coin.png', 390 + i * 40, 340, 40, 40))
            coins.add(GameSprite('images/coin.png', 390 + i * 40, 420, 40, 40))

        for i in range(2):
            coins.add(GameSprite('images/coin.png', 600 + i * 60, 370, 40, 40))
        for i in range(2):
            coins.add(GameSprite('images/coin.png', 850 + i * 60, 320, 40, 40))
        for i in range(2):
            coins.add(GameSprite('images/coin.png', 1100 + i * 60, 280, 40, 40))

        monsters.add(Enemy_h('images/enemy.png', 400, 470, 80, 80, 3, 350, 500))
        monsters.add(Enemy_h('images/enemy.png', 650, 420, 80, 80, 3, 600, 750))
        monsters.add(Enemy_v('images/enemy.png', 950, 150, 80, 80, 2, 100, 300))

        hero = Player('images/Harry.png', hero_x, hero_y, hero_size_x, hero_size_y, 0, 0)
        final_sprite = GameSprite('images/door.png', 1150, 250, 100, 100)

    elif level_name == "lvl5":
        base_platform = GameSprite('images/wall2.png', 0, 650, win_width, 50)
        platforms.add(base_platform)

        platforms.add(GameSprite('images/platform.png', 150, 520, 180, 30))
        platforms.add(GameSprite('images/platform.png', 450, 480, 180, 30))
        platforms.add(GameSprite('images/platform.png', 750, 520, 180, 30))
        platforms.add(GameSprite('images/platform.png', 1050, 480, 180, 30))
        platforms.add(GameSprite('images/platform.png', 300, 350, 150, 30))
        platforms.add(GameSprite('images/platform.png', 600, 300, 150, 30))
        platforms.add(GameSprite('images/platform.png', 900, 350, 150, 30))

        coins.add(GameSprite('images/coin.png', 560, 180, 40, 40))
        coins.add(GameSprite('images/coin.png', 640, 150, 40, 40))
        coins.add(GameSprite('images/coin.png', 720, 180, 40, 40))

        for i in range(5):
            coins.add(GameSprite('images/coin.png', 560 + i * 40, 220, 40, 40))

        for i in range(2):
            coins.add(GameSprite('images/coin.png', 180 + i * 60, 490, 40, 40))
        for i in range(2):
            coins.add(GameSprite('images/coin.png', 480 + i * 60, 450, 40, 40))
        for i in range(2):
            coins.add(GameSprite('images/coin.png', 780 + i * 60, 490, 40, 40))
        for i in range(2):
            coins.add(GameSprite('images/coin.png', 1080 + i * 60, 450, 40, 40))

        coins.add(GameSprite('images/coin.png', 350, 320, 40, 40))
        coins.add(GameSprite('images/coin.png', 650, 270, 40, 40))
        coins.add(GameSprite('images/coin.png', 950, 320, 40, 40))

        monsters.add(Enemy_h('images/enemy.png', 250, 490, 80, 80, 2, 150, 350))
        monsters.add(Enemy_h('images/enemy.png', 850, 490, 80, 80, 2, 750, 950))

        hero = Player('images/Harry.png', hero_x, hero_y, hero_size_x, hero_size_y, 0, 0)
        final_sprite = GameSprite('images/door.png', 640, 570, 100, 100)

    if hero:
        for skin in shop_skins:
            if skin.active:
                hero.apply_skin(skin.name)
                break

        for boost in shop_boosts:
            if boost.active and boost.unlocked:
                if boost.name == "Double Jump":
                    hero.double_jump = True
                elif boost.name == "High Jump":
                    hero.high_jump = True
                elif boost.name == "Speed Boost":
                    hero.fast_move = True
                elif boost.name == "Shield":
                    hero.shield = True
                elif boost.name == "Triple Shot":
                    hero.multi_bullet = True

    return hero, final_sprite

def show_level_progress(level_name, collected_coins, total_coins):
    level_font = font.SysFont('Arial', 30)
    level_text = level_font.render(f"Level: {level_name.replace('lvl', '')}", True, (255, 255, 255))
    window.blit(level_text, (20, 20))

    coin_font = font.SysFont('Arial', 30)
    coin_text = coin_font.render(f"Coins: {collected_coins}/{total_coins}", True, (255, 215, 0))
    window.blit(coin_text, (20, 60))


def show_shop_interface(active_tab="boosts"):
    window.blit(shop_background, (0, 0))

    shop_back_but.reset()

    boosts_tab_but.reset()
    skins_tab_but.reset()

    coin_font = font.SysFont('Arial', 36)
    coin_text = coin_font.render(f"Coins: {player_coins}", True, (255, 215, 0))
    window.blit(coin_text, (win_width - 200, 20))

    items_to_display = shop_boosts if active_tab == "boosts" else shop_skins

    item_name_font = font.SysFont('Arial', 24)
    item_desc_font = font.SysFont('Arial', 18)
    button_font = font.SysFont('Arial', 20)

    y_offset = 150
    for item in items_to_display:
        draw.rect(window, (200, 200, 200), (50, y_offset, win_width - 100, 100), 2)

        try:
            item_img = transform.scale(image.load(item.image_path), (80, 80))
            window.blit(item_img, (70, y_offset + 10))
        except:
            draw.rect(window, (150, 150, 150), (70, y_offset + 10, 80, 80))

        item_name = item_name_font.render(item.name, True, (255, 255, 255))
        item_desc = item_desc_font.render(item.description, True, (200, 200, 200))

        window.blit(item_name, (170, y_offset + 20))
        window.blit(item_desc, (170, y_offset + 50))

        if item.unlocked:
            if item.active:
                status_text = item_name_font.render("ACTIVE", True, (0, 255, 0))
                window.blit(status_text, (win_width - 200, y_offset + 20))
                draw.rect(window, (100, 100, 100), (win_width - 200, y_offset + 50, 120, 30))
                deactivate_button = button_font.render("Deactivate", True, (255, 0, 0))
                window.blit(deactivate_button, (win_width - 190, y_offset + 55))
            else:
                status_text = item_name_font.render("OWNED", True, (0, 200, 255))
                window.blit(status_text, (win_width - 200, y_offset + 20))
                draw.rect(window, (100, 100, 100), (win_width - 200, y_offset + 50, 120, 30))
                activate_button = button_font.render("Activate", True, (0, 255, 0))
                window.blit(activate_button, (win_width - 180, y_offset + 55))
        else:
            price_text = item_name_font.render(f"Price: {item.price}", True, (255, 215, 0))
            window.blit(price_text, (win_width - 200, y_offset + 20))

            draw.rect(window, (100, 100, 100), (win_width - 200, y_offset + 50, 80, 30))
            buy_button = button_font.render("Buy", True, (255, 255, 255))
            window.blit(buy_button, (win_width - 180, y_offset + 55))

        y_offset += 120


def handle_shop_clicks(mouse_pos, active_tab):
    global player_coins, hero, active_skin

    if shop_back_but.rect.collidepoint(mouse_pos):
        return "back_to_menu"

    if boosts_tab_but.rect.collidepoint(mouse_pos):
        return "tab_boosts"

    if skins_tab_but.rect.collidepoint(mouse_pos):
        return "tab_skins"

    items_to_check = shop_boosts if active_tab == "boosts" else shop_skins

    y_offset = 150
    for item in items_to_check:
        item_rect = Rect(50, y_offset, win_width - 100, 100)

        if item_rect.collidepoint(mouse_pos):
            if item.unlocked:
                button_rect = Rect(win_width - 200, y_offset + 50, 120, 30)
                if button_rect.collidepoint(mouse_pos):
                    if active_tab == "boosts":
                        if item.active:
                            item.active = False
                            deactivate_boost(item.name)
                        else:
                            if item.name in ["Double Jump", "High Jump"]:
                                for boost in shop_boosts:
                                    if boost.name in ["Double Jump", "High Jump"] and boost != item:
                                        boost.active = False
                                        deactivate_boost(boost.name)
                                        
                            item.active = True
                            activate_boost(item.name)

                    elif active_tab == "skins":
                        if not item.active:

                            for skin in shop_skins:
                                skin.active = False
                            item.active = True
                            active_skin = item.name

                            if hero:
                                hero.apply_skin(item.name)
            else:
                buy_button_rect = Rect(win_width - 200, y_offset + 50, 80, 30)
                if buy_button_rect.collidepoint(mouse_pos) and player_coins >= item.price:
                    player_coins -= item.price
                    item.unlocked = True

                    if active_tab == "skins":
                        for skin in shop_skins:
                            if skin != item:
                                skin.active = False
                        item.active = True
                        active_skin = item.name
                        if hero:
                            hero.apply_skin(item.name)

        y_offset += 120

    return active_tab


def activate_boost(boost_name):
    global hero
    if not hero:
        return

    if boost_name == "Double Jump":
        hero.double_jump = True
        if hero.high_jump:
            hero.high_jump = False
            for boost in shop_boosts:
                if boost.name == "High Jump":
                    boost.active = False
    elif boost_name == "High Jump":
        hero.high_jump = True
        if hero.double_jump:
            hero.double_jump = False
            for boost in shop_boosts:
                if boost.name == "Double Jump":
                    boost.active = False
    elif boost_name == "Speed Boost":
        hero.fast_move = True
    elif boost_name == "Shield":
        hero.shield = True
    elif boost_name == "Triple Shot":
        hero.multi_bullet = True


def deactivate_boost(boost_name):
    global hero
    if not hero:
        return

    if boost_name == "Double Jump":
        hero.double_jump = False
    elif boost_name == "High Jump":
        hero.high_jump = False
    elif boost_name == "Speed Boost":
        hero.fast_move = False
    elif boost_name == "Shield":
        hero.shield = False
    elif boost_name == "Triple Shot":
        hero.multi_bullet = False


def show_menu():
    window.blit(menu_background, (0, 0))

    title_font = font.SysFont('Arial', 72)
    title_text = title_font.render("PLATFORMER", True, (255, 215, 0))
    window.blit(title_text, (win_width // 2 - title_text.get_width() // 2, 100))

    start_button.reset()
    shop_button.reset()
    exit_button.reset()


def handle_menu_clicks(mouse_pos):
    if start_button.rect.collidepoint(mouse_pos):
        return "start_game"

    if shop_button.rect.collidepoint(mouse_pos):
        return "open_shop"

    if exit_button.rect.collidepoint(mouse_pos):
        return "exit"

    return "menu"


def show_level_completed():
    global level_coins, total_level_coins

    window.blit(level_complete_background, (0, 0))

    title_font = font.SysFont('Arial', 72)
    title_text = title_font.render("LEVEL COMPLETED!", True, (0, 255, 0))
    window.blit(title_text, (win_width // 2 - title_text.get_width() // 2, 100))

    stats_font = font.SysFont('Arial', 36)
    coins_text = stats_font.render(f"Coins collected: {level_coins}/{total_level_coins}", True, (255, 215, 0))
    window.blit(coins_text, (win_width // 2 - coins_text.get_width() // 2, 200))

    if level_coins == total_level_coins:
        bonus_text = stats_font.render("PERFECT! Bonus: +10 coins", True, (0, 255, 0))
        window.blit(bonus_text, (win_width // 2 - bonus_text.get_width() // 2, 250))

    next_level_button.reset()
    menu_button.reset()


def handle_level_completed_clicks(mouse_pos):
    if next_level_button.rect.collidepoint(mouse_pos):
        return "next_level"

    if menu_button.rect.collidepoint(mouse_pos):
        return "menu"

    return "level_completed"


def show_game_over():
    window.blit(game_over_background, (0, 0))

    retry_button.reset()
    menu_button_2.reset()


def handle_game_over_clicks(mouse_pos):
    if retry_button.rect.collidepoint(mouse_pos):
        return "retry_level"

    if menu_button_2.rect.collidepoint(mouse_pos):
        return "menu"

    return "game_over"

    price_text = item_name_font.render(f"Price: {item.price}", True, (255, 215, 0))
    window.blit(price_text, (win_width - 200, y_offset + 40))

    buy_button = font.SysFont('Arial', 20).render("Buy", True, (255, 255, 255))
    draw.rect(window, (100, 100, 100), (win_width - 100, y_offset + 30, 80, 40))
    window.blit(buy_button, (win_width - 80, y_offset + 40))


def show_victory_screen():
    s = Surface((win_width, win_height))
    s.fill((0, 0, 0))
    s.set_alpha(230)
    window.blit(s, (0, 0))

    victory_font_big = font.SysFont('Arial', 64)
    victory_font = font.SysFont('Arial', 36)

    title_text = victory_font_big.render("ПОЗДРАВЛЯЕМ!", True, (255, 215, 0))
    message_text = victory_font.render("Вы прошли все уровни игры!", True, (255, 255, 255))

    window.blit(title_text, (win_width // 2 - title_text.get_width() // 2, 200))
    window.blit(message_text, (win_width // 2 - message_text.get_width() // 2, 300))

    return_menu_button = GameSprite('images/button_return.png', win_width // 2 - 220, 400, 200, 60)
    restart_button = GameSprite('images/button_restart.png', win_width // 2 + 20, 400, 200, 60)

    return_menu_button.reset()
    restart_button.reset()

    button_font = font.SysFont('Arial', 24)
    menu_text = button_font.render("В МЕНЮ", True, (0, 0, 0))
    restart_text = button_font.render("НАЧАТЬ СНАЧАЛА", True, (0, 0, 0))

    window.blit(menu_text, (win_width // 2 - 190, 415))
    window.blit(restart_text, (win_width // 2 + 45, 415))

    return return_menu_button, restart_button


init()

win_width = 1400
win_height = 800

window = display.set_mode((win_width, win_height))
display.set_caption("Platformer")

background = transform.scale(image.load('images/menu.png'), (win_width, win_height))
menu_background = transform.scale(image.load('images/bg.png'), (win_width, win_height))
shop_background = transform.scale(image.load('images/shop_bg.png'), (win_width, win_height))
level_complete_background = transform.scale(image.load('images/menu.png'), (win_width, win_height))
game_over_background = transform.scale(image.load('images/game_over.png'), (win_width, win_height))

start_button = GameSprite('images/start_hover.png', 700, 405, 250, 100)
shop_button = GameSprite('images/shop_button.png', 400, 400, 250, 250)
exit_button = GameSprite('images/Exit_hover.png', 700, 550, 250, 100)

next_level_button = GameSprite('images/next_level_button.png', win_width // 2 - 120, 450, 240, 80)
menu_button = GameSprite('images/menu_button.png', win_width // 2 - 100, 550, 200, 80)

retry_button = GameSprite('images/replay_button.png', win_width // 2 - 100, 450, 200, 80)
menu_button_2 = GameSprite('images/menu_button.png', win_width // 2 - 100, 550, 200, 80)

shop_back_but = GameSprite('images/back_button.png', 20, 20, 100, 50)
boosts_tab_but = GameSprite('images/boost_tab.png', 200, 80, 150, 50)
skins_tab_but = GameSprite('images/skins_tab.png', 380, 80, 150, 50)

barriers = sprite.Group()
platforms = sprite.Group()
monsters = sprite.Group()
coins = sprite.Group()
bullets = sprite.Group()


player_coins = 0
level_coins = 0
total_level_coins = 0


current_level = "lvl1"


shop_boosts = [
    ShopItem("Double Jump", "Allows you to jump twice in air", 30, "images/boost_doublejump.png"),
    ShopItem("High Jump", "Jump 30% higher", 25, "images/boost_highjump.png"),
    ShopItem("Speed Boost", "Move 50% faster", 25, "images/boost_speed.png"),
    ShopItem("Shield", "Protects from one enemy hit", 40, "images/boost_shield.png"),
    ShopItem("Triple Shot", "Shoot three bullets at once", 35, "images/boost_tripleshot.png")
]


shop_skins = [
    ShopItem("Harry", "Default hero skin", 0, "images/Harry.png", "skin", True),
    ShopItem("Hermiona", "Hermiona hero skin", 20, "images/Hermiona.png", "skin"),
    ShopItem("Ron", "Ron hero skin", 20, "images/Ron.png", "skin"),
    ShopItem("Damboldor", "Damboldor hero skin", 20, "images/Damboldor.png", "skin"),
    ShopItem("Profesor", "Profesor hero skin", 20, "images/Profesor.png", "skin"),
]


active_skin = "hero"
shop_skins[0].active = True


hero, final_sprite = create_level(current_level)


jump_sound = mixer.Sound('sounds/jump.wav')
shoot_sound = mixer.Sound('sounds/shoot.wav')
coin_sound = mixer.Sound('sounds/coin.wav')
hit_sound = mixer.Sound('sounds/hit.wav')
win_sound = mixer.Sound('sounds/win.wav')
lose_sound = mixer.Sound('sounds/over.wav')


mixer.music.load('sounds/main.wav')
mixer.music.play(-1)  


game_state = "menu"
shop_tab = "boosts"
run = True
clock = time.Clock()

jump_key_pressed = False


while run:
    for e in event.get():
        if e.type == QUIT:
            run = False


        elif e.type == KEYDOWN:
            if game_state == "game":
                if e.key == K_a or e.key == K_LEFT:
                    hero.x_speed = -8
                elif e.key == K_d or e.key == K_RIGHT:
                    hero.x_speed = 8
                elif (e.key == K_w or e.key == K_UP or e.key == K_SPACE) and not jump_key_pressed:
                    jump_key_pressed = True
                    hero.jump()
                    jump_sound.play()
                elif e.key == K_LCTRL:
                    hero.fire()
                    shoot_sound.play()


        elif e.type == KEYUP:
            if game_state == "game":
                if e.key == K_a or e.key == K_LEFT or e.key == K_d or e.key == K_RIGHT:
                    hero.x_speed = 0
                elif e.key == K_w or e.key == K_UP or e.key == K_SPACE:
                    jump_key_pressed = False

        elif e.type == MOUSEBUTTONDOWN:
            if e.button == 1:
                if game_state == "menu":
                    action = handle_menu_clicks(mouse.get_pos())
                    if action == "start_game":
                        game_state = "game"
                        current_level = "lvl1"
                        hero, final_sprite = create_level(current_level)
                    elif action == "open_shop":
                        game_state = "shop"
                        shop_tab = "boosts"
                    elif action == "exit":
                        run = False

                elif game_state == "shop":
                    action = handle_shop_clicks(mouse.get_pos(), shop_tab)
                    if action == "back_to_menu":
                        game_state = "menu"
                    elif action == "tab_boosts":
                        shop_tab = "boosts"
                    elif action == "tab_skins":
                        shop_tab = "skins"

                elif game_state == "level_completed":
                    action = handle_level_completed_clicks(mouse.get_pos())
                    if action == "next_level":
                        level_num = int(current_level.replace("lvl", ""))
                        if level_num < 5:
                            current_level = f"lvl{level_num + 1}"
                            hero, final_sprite = create_level(current_level)
                            game_state = "game"
                        else:
                            game_state = "menu"
                    elif action == "menu":
                        game_state = "menu"

                elif game_state == "game_over":
                    action = handle_game_over_clicks(mouse.get_pos())
                    if action == "retry_level":
                        hero, final_sprite = create_level(current_level)
                        game_state = "game"
                    elif action == "menu":
                        game_state = "menu"


    if game_state == "menu":
        show_menu()

    elif game_state == "shop":
        show_shop_interface(shop_tab)

    elif game_state == "game":

        window.blit(background, (0, 0))


        bullets.update()
        bullets.draw(window)


        sprite_list = sprite.groupcollide(bullets, monsters, True, True)


        coins_collected = sprite.spritecollide(hero, coins, True)
        for coin in coins_collected:
            player_coins += 1
            coin_sound.play()

        monster_hit = sprite.spritecollide(hero, monsters, False)
        if monster_hit:
            if hero.shield:
                hero.shield = False

                for boost in shop_boosts:
                    if boost.name == "Shield":
                        boost.active = False

                monster_hit[0].kill()  
                hit_sound.play()
            else:
                game_state = "game_over"
                lose_sound.play()

        if sprite.collide_rect(hero, final_sprite):
            game_state = "level_completed"
            level_coins = player_coins
            total_level_coins = len(coins) + level_coins

        monsters.update()


        if hero.update(barriers, platforms):
            game_state = "game_over"
            lose_sound.play()


        platforms.draw(window)
        barriers.draw(window)
        coins.draw(window)
        monsters.draw(window)
        final_sprite.reset()
        hero.reset()


        show_level_progress(current_level, player_coins, len(coins) + player_coins)

    elif game_state == "level_completed":
        show_level_completed()

    elif game_state == "game_over":
        show_game_over()


    display.update()
    clock.tick(60)
