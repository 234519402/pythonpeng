import sys
from time import sleep
import json
from pathlib import Path
import pygame
from random import randint

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from star import Star

class AlienInvasion:

    def __init__(self):
            
        if sys.platform == 'win32':
            pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init() # 初始化pygame
        self.clock = pygame.time.Clock() # 创建一个时钟
        self.settings = Settings() # 创建一个设置对象

        self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion") # 设置窗口标题

        self.stats = GameStats(self) # 创建一个统计对象
        self.sb = Scoreboard(self) # 创建一个分数对象

        self.ship = Ship(self)  # 创建飞船对象
        self.bullets = pygame.sprite.Group() # 创建子弹组
        self.aliens = pygame.sprite.Group() # 创建外星人组
        self.stars = pygame.sprite.Group() # 创建星星组

        self._create_fleet() # 创建外星人群

        # 创建开始按钮
        self.play_button = Button(self, "start")

        # 游戏开始时处于非活动状态
        self.game_active = False

    def run_game(self):
        """开始游戏的主循环"""
        while True:
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()
            self.clock.tick(60)
    def _check_play_button(self, mouse_pos):
        """当玩家点击Play按钮时开始新游戏"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self._start_game()

    def _start_game(self):
        """开始一场新的游戏"""
        # 重置游戏设置
        self.settings.initialize_dynamic_settings()

        #  重置游戏统计数据
        self.stats.reset_stats()
        self.game_active = True
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()

        #清空剩余的外星人和子弹
        self.aliens.empty()
        self.bullets.empty()
    
        
        # 创建一个新的舰队并使飞船居中
        self._create_fleet()
        self.ship.center_ship()

        # 隐藏鼠标光标
        pygame.mouse.set_visible(False)
    
    def _close_game(self):
        """保存最高分并退出游戏"""
        saved_high_score = self.stats.get_saved_high_score()
        if self.stats.high_score > saved_high_score:
            path = Path('high_score.txt')
            contents = json.dumps(self.stats.high_score)
            path.write_text(contents)
        
        sys.exit()
    
    def _update_screen(self):
        """更新屏幕上的图像，并切换到新的屏幕"""
        self.screen.fill(self.settings.bg_color)
        
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.stars.draw(self.screen)

        # 绘制分数信息
        self.sb.show_score()

        #如果游戏非活动状态，绘制播放按钮
        if not self.game_active:
            self.play_button.draw_button()

        pygame.display.flip()


    def _check_events(self):
        """响应按键和鼠标事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._close_game()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                
    def _check_keydown_events(self, event):
        """响应按键事件"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            self._close_game()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p and not self.game_active:
            self._start_game()

    def _check_keyup_events(self, event):
        """响应键盘松开事件"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """创建一个新的子弹并将其添加到子弹组中"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """更新子弹的位置并移除过期的子弹"""
        # 更新子弹的位置
        self.bullets.update()

        #移除已经消失的子弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _update_aliens(self):
        """检查舰队是否到达边缘，然后更新所有飞碟的位置 """
        self._check_fleet_edges()
        self.aliens.update()

        # 查找飞碟与飞船的碰撞
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # 查找飞碟到达屏幕底部
        self._check_aliens_bottom()

    def _create_fleet(self):
        """创建外星人舰队"""
        # 创建一个外星人并找到一排中的外星人数量
        # 每两个外星人间距等于一个外星人宽度
        alien = Alien(self)         
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        #确定适合在屏幕上显示的外星人行数 
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                                (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        
        #创建全部外星人舰队
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """创建一个外星人并将其放置在行中"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)
    def _check_fleet_edges(self):
        """检查是否有外星人到达了边缘，做出相应处理"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
            
    def _change_fleet_direction(self):
        """使整个舰队掉落并改变舰队的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
        
    def _ship_hit(self):
        """对飞船被外星人击中进行响应"""
        if self.stats.ships_left > 0:
            #减少剩余飞船数量，并更新计分板
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            
            # 清空所有剩余外星人和子弹
            self.aliens.empty()
            self.bullets.empty()
            
            #创建一个新的舰队并居中飞船
            self._create_fleet()
            self.ship.center_ship()
            
            # Pause.
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)
    def _check_aliens_bottom(self):
        """检查是否有外星人到达了屏幕底部"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # 将此视作飞船中弹，进行处理
                self._ship_hit()
                break
        
    def _check_bullet_alien_collisions(self):
        """处理子弹与外星人的碰撞"""
        # 移除发生碰撞的子弹和外星人
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            #如果外星人已经全部移除，则销毁现有子弹并创建新的舰队，同时增加游戏速度
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # 增加关卡数并更新关卡显示
            self.stats.level += 1
            self.sb.prep_level()

    def _create_star(self):
        """创建背景星星"""
        i = 1
        while i <= 15:
            new_star = Star(self)
            x_star = randint(20,1180)
            y_star = randint(20,780)
            new_star.rect.x = x_star
            new_star.rect.y = y_star
            self.stars.add(new_star)
            i += 1

    

if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
