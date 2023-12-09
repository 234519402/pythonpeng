#存储外星人入侵小游戏的所有设置的类
class Settings:
    def __init__(self):
        #初始化游戏的静态设置
        #屏幕设置
        self.screen_width = 1200 # 屏幕宽度
        self.screen_height = 700 # 屏幕高度
        self.bg_color = (230, 230, 230) # 背景颜色

        self.ship_limit = 2 # 生命数量

        self.bullet_width = 3 # 子弹宽度
        self.bullet_height = 15 # 子弹高度
        self.bullet_color = (0, 150, 150) # 子弹颜色
        self.bullets_allowed = 10 # 子弹数量

        self.fleet_drop_speed = 10  # 外星人掉落速度

        self.speedup_scale = 1.1    # 加快速度的比例
        self.score_scale = 1.1  # 加快得分的比例

        self.initialize_dynamic_settings() # 初始化动态设置

    def initialize_dynamic_settings(self):
        #初始化游戏的动态设置
        self.ship_speed = 4.0   # 飞船速度
        self.bullet_speed = 9.0 # 子弹速度
        self.alien_speed = 1.5  # 外星人速度

        self.fleet_direction = 1 # 外星人掉落方向

        self.alien_points = 100      # 外星人得分

    def increase_speed(self):   
        self.ship_speed *= self.speedup_scale      # 加快飞船速度
        self.bullet_speed *= self.speedup_scale    # 加快子弹速度
        self.alien_speed *= self.speedup_scale     # 加快外星人速度

        self.alien_points = int(self.alien_points * self.score_scale) # 加快得分
