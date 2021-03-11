import pygame
import sys
import random

pygame.init()
GameCaption = "Doodle Jump"
ScreenSize = (800, 800)
Screen = pygame.display.set_mode(ScreenSize)
GridSize = (14, 14)
WordSize = (25, 25)
ColorFloral = (255, 250, 240)  # for screen
ColorKhaki = (240, 230, 140)  # for grid
ColorBlack = (0, 0, 0)  # for score
MaxVel = 20
LEFT = 0
RIGHT = 1
XSpeed=15
MaxScore=0

class Platform:

	images = [
		pygame.image.load("assets/platform_green.png").convert_alpha(),
		pygame.image.load("assets/platform_blue.png").convert_alpha(),
		pygame.image.load("assets/platform_red.png").convert_alpha(),
		pygame.image.load("assets/platform_red_break.png").convert_alpha(),
	]
	height = images[0].get_height()
	width = images[0].get_width()

	def __init__(self, x, y, platform_type=None):
		self.x = x
		self.y = y
		if platform_type is None:
			rand=random.randint(1,10)
			if rand<9:
				platform_type=0
			elif rand==9:
				platform_type=1
			else:
				platform_type=2
		self.type = platform_type  # 0:綠色 1:藍色 2:紅色
		self.dir = LEFT  # For 藍色跳板
		self.is_break = False  # For 紅色跳板

	def _get_image(self):
		if self.is_break==True:
			return self.images[3]
		return self.images[self.type]

	def get_rect(self):
		return pygame.Rect(self.x, self.y, self.width, self.height)

	def draw(self, screen, screen_y):
		img = self._get_image()
		screen.blit(img,(self.x,self.y-screen_y))

class Player:

	images = [
		pygame.image.load("assets/player_left.png").convert_alpha(),
		pygame.image.load("assets/player_right.png").convert_alpha(),
		pygame.image.load("assets/player_left_jump.png").convert_alpha(),
		pygame.image.load("assets/player_right_jump.png").convert_alpha(),
	]
	height = images[0].get_height()
	width = images[0].get_width()

	def __init__(self):
		self.x = 400
		self.y = 400
		self.direction = 0
		self.movement = 0  # screen x: loop
		self.velocity = 0
		self.gravity = -1

	def _get_image(self):
		# 要根據 direction 改
		if self.direction==0:
			if self.velocity>0:
				player_type=0
			else:
				player_type=2
		else:
			if self.velocity>0:
				player_type=1
			else:
				player_type=3
		return self.images[player_type]

	def draw(self, screen, screen_y):
		screen.blit(self._get_image(), (self.x, self.y - screen_y))

	def go_right(self):
		self.direction=RIGHT
		self.movement=XSpeed

	def go_left(self):
		self.direction=LEFT
		self.movement=-XSpeed

	def no_action(self):
		# 沒有按鍵時讓左右移動漸漸歸零
		if self.movement > 0:
			self.movement -= 1
		elif self.movement < 0:
			self.movement += 1

	def get_rect(self):
		return pygame.Rect(self.x, self.y, self.width, self.height)

	def move(self):
		self.x+=self.movement
		if self.x<-Player.width//2:
			self.x+=ScreenSize[0]
		if self.x>ScreenSize[0]-Player.width//2:
			self.x-=ScreenSize[0]

		if self.velocity > -MaxVel:
			self.velocity += self.gravity
		self.y -= self.velocity


class Spring:
	images = [
		pygame.image.load("assets/spring.png").convert_alpha(),
		pygame.image.load("assets/spring_bounce.png").convert_alpha(),
	]
	height = images[0].get_height()
	width = images[0].get_width()

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.type = 0

	def draw(self, screen, screen_y):
		if self.type==0:
			screen.blit(self.images[0],(self.x,self.y-screen_y))
		else:
			screen.blit(self.images[1],(self.x,self.y-screen_y))

	def get_rect(self):
		return pygame.Rect(self.x, self.y, self.width, self.height)


class DoodleJump:

	def __init__(self):
		### control the game
		self.platforms = []  # positions of platforms
		self.springs = []  # positions of springs
		self.player = Player()
		self.score = 0
		self.screen_y = 0  # screen y: roll

		### draw the screen
		self.screen = Screen
		self.clock = pygame.time.Clock()
		self.font = pygame.font.SysFont("Arial", 25)

		pygame.display.set_caption(GameCaption)

	def update_player(self):
		key = pygame.key.get_pressed()
		if key[pygame.K_RIGHT]:
			self.player.go_right()
		elif key[pygame.K_LEFT]:
			self.player.go_left()
		else:
			self.player.no_action()

		self.player.move()
		### screen y: roll
		if self.player.y-self.screen_y<400:
			self.screen_y-=400-(self.player.y-self.screen_y)
		### draw the player
		self.player.draw(self.screen, self.screen_y)

	def update_platforms(self):
		rect_player = self.player.get_rect()
		for p in self.platforms:
			### collide with the platform
			#rect_platform = p.get_rect()
			#if rect_platform.colliderect(rect_player) and self.player.velocity < 0 and (self.player.y + Player.height - 15) <= (p.y - self.screen_y):
			if self.player.velocity<0 and -11<self.player.y+Player.height-p.y<11 and -Player.width<self.player.x-p.x<Platform.width:
				# 處理碰撞
				# if red: break
				if p.type==2:
					p.is_break=True
				else:
					self.player.velocity=MaxVel
			### if blue: move
			if p.type==1:
				if p.x<0:
					p.dir=LEFT
				if p.x>ScreenSize[0]-Platform.width:
					p.dir=RIGHT
				if p.dir==LEFT:
					p.x+=XSpeed
				if p.dir==RIGHT:
					p.x-=XSpeed

		for s in self.springs:
			### collide with the spring
			#rect_spring = s.get_rect()
			#if rect_spring.colliderect(rect_player) and self.player.velocity < 0 and (self.player.y + Player.height - 15) <= (s.y - self.screen_y):
			if self.player.velocity<0 and -11<self.player.y+Player.height-s.y<11 and -Player.width<self.player.x-s.x<Spring.width:
				self.player.velocity=MaxVel*1.5
				s.type=1

	def draw_platforms(self):
		### draw platforms
		for p in self.platforms:
			next_y = self.platforms[0].y - self.screen_y
			if next_y > ScreenSize[1]:
				### add a new platform
				x = random.randint(Platform.width//2,ScreenSize[0]-Platform.width//2)
				y = self.platforms[-1].y-50
				new_platform = Platform(x, y)
				self.platforms.append(new_platform)

				### add a spring
				if new_platform.type==0:
					rand=random.randint(1,5)
					if rand==1:
						new_spring=Spring(random.randint(x,x+Platform.width-Spring.width),y-Spring.height)
						self.springs.append(new_spring)

				self.platforms.pop(0)  # delete the old platform
				self.score += 100  # renew the score
			p.draw(self.screen, self.screen_y)

		### draw springs
		for s in self.springs:
			s.draw(self.screen, self.screen_y)

	def draw_background(self):
		### fill color
		self.screen.fill(ColorFloral)
		### draw grids
		i=0
		while i<ScreenSize[0]:
			pygame.draw.line(self.screen,ColorKhaki,(i,0),(i,ScreenSize[1]))
			i+=GridSize[0]
		i=0
		while i<ScreenSize[1]:
			pygame.draw.line(self.screen,ColorKhaki,(0,i),(ScreenSize[0],i))
			i+=GridSize[1]

	def generate_platforms(self):
		y = ScreenSize[1]
		while y >= -50:
			if y == 500:  # the first platform on which the player stands
				x = 400
				self.platforms.append(Platform(x, y, 0))
			else:  # generate random x
				x=random.randint(Platform.width//2,ScreenSize[0]-Platform.width//2)
				self.platforms.append(Platform(x, y))
			y -= 50

	def run(self):
		global MaxScore
		### init the game
		self.generate_platforms()
		while True:
			### close the game
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
			### restart the game
			if self.player.y-self.screen_y>ScreenSize[1]:
				if self.score>MaxScore:
					MaxScore=self.score
				pygame.init()
				DoodleJump().run()
			### update the game
			self.draw_background()
			self.draw_platforms()
			self.update_player()
			self.update_platforms()
			self.screen.blit(self.font.render("Maxscore:"+str(MaxScore)+" Score:"+str(self.score), -1, ColorBlack), WordSize)
			pygame.display.flip()
			self.clock.tick(60)

DoodleJump().run()
