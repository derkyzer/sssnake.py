
## Module Import and Initialization

import pygame
from random import randint
pygame.init()
delay_timer = pygame.time.Clock()
fps = pygame.time.Clock()

##############################################################################################################################
#     CUSTOMIZABLE SETTINGS     #
#################################

grid_size = [7,10]			## To make the start screen more beautiful, make this: [odd number,even number]
box_size = 75				## 50-100 recommended.

bg_color = "gray12"			## Background color.
fg_color = "gray96"			## Snake/text color.
fg_color_2 = "gray66"		## Inactive text button color.
sp_color = "firebrick"		## Snake's objective/special text color.

font_name = "calibri"		## Some standard fonts might be: calibri, candara, verdana, arial, trebuchetms, corbel...

##############################################################################################################################
#    DEFAULT LAUNCH SETTINGS    #
#################################

speed = 5.0
loop_screen = False
manual_move = False
god_mode = False
immortal = False
save_cheat_scores = False

##############################################################################################################################
#         EXPERIMENTAL          #
#################################

fullscreen = False			## This will change the grid to fit your screen, but box_size will stay the same.
trails = False				## Leaves a trail behind the snake.

## Dictionaries

deltas = {"up":   [ 0,-1],
		  "down": [ 0, 1],
		  "left": [-1, 0],
		  "right":[ 1, 0]}

direction_keys = {pygame.K_UP:"up",
				  pygame.K_w:"up",
				  pygame.K_DOWN:"down",
				  pygame.K_s:"down",
				  pygame.K_LEFT:"left",
				  pygame.K_a:"left",
				  pygame.K_RIGHT:"right",
				  pygame.K_d:"right"}

## Objects

class WindowObj:
	def __init__(self):
		self.color = bg_color
		self.size = [box_size*grid_wh for grid_wh in grid_size]
		if fullscreen: self.surface = pygame.display.set_mode(self.size,pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF,vsync=1)
		else: self.surface = pygame.display.set_mode(self.size,vsync=1)
		pygame.display.set_caption('SSSNAKE.py')

class GridObj:
	def __init__(self,box_id):
		self.color = bg_color
		self.swap_pallette = {fg_color:bg_color,bg_color:fg_color,sp_color:fg_color}
		self.box_id = box_id
	def draw(self,surface,force_color=False):
		pygame.draw.rect(surface,[force_color,self.color][not force_color],[[(box_size*self.box_id[box_xy])+[play_rect.x,play_rect.y][box_xy] for box_xy in range(2)],[box_size,box_size]])
		if self.color == bg_color and trails:	## Might be less intense to reset the trail after the objective is completed.
			pygame.draw.rect(surface,fg_color,[[(box_size*self.box_id[box_xy])+[play_rect.x,play_rect.y][box_xy]+box_size*.25 for box_xy in range(2)],[box_size*.5,box_size*.5]])
	def switch(self,surface,swap_colors=True,custom_color=False):
		self.color = [custom_color,[self.color,self.swap_pallette[self.color]][swap_colors]][not custom_color]
		self.draw(surface)
		return(self.box_id)

class TextObj:
	def __init__(self,window_size,string,color=fg_color,y_offset=0,string_additions=[],is_bold=False,relative_font_size=1,x_alignment="m"):
		self.base_string = string
		self.color = color
		self.alignment = x_alignment
		try: self.font = pygame.font.SysFont(font_name,round((grid_size[[0,1][grid_size[0]>=grid_size[1]]]*box_size*relative_font_size)/10),bold=is_bold)
		except: self.font = pygame.font.SysFont("default",round((grid_size[[0,1][grid_size[0]>=grid_size[1]]]*box_size*relative_font_size)/10),bold=is_bold)
		self.window_size = window_size
		self.y_offset = y_offset
		self.enabled = False
		if not string_additions:
			self.string = self.base_string
			self.text = self.font.render(self.string,True,self.color)
			self.text_rect = self.alignTextRect()
	def alignTextRect(self):
		if self.alignment == "l":
			return(self.text.get_rect(midright=(self.window_size[0]/2,self.window_size[1]/2+self.y_offset)))
		elif self.alignment == "r":
			return(self.text.get_rect(midleft=(self.window_size[0]/2,self.window_size[1]/2+self.y_offset)))
		else:
			return(self.text.get_rect(center=(self.window_size[0]/2,self.window_size[1]/2+self.y_offset)))
	def draw(self,surface,change_color=False,string_additions=[],y_offset=0):
		if y_offset:
			self.y_offset = y_offset
			self.text_rect = self.alignTextRect()
		if string_additions:
			self.string = self.base_string + " ".join(string_additions)
			self.text = self.font.render(self.string,True,self.color)
			self.text_rect = self.alignTextRect()
		if change_color:
			self.color = change_color
			self.text = self.font.render(self.string,True,self.color)
		surface.blit(self.text,self.text_rect)

class SnakeObj:
	def __init__(self,speed=speed,cheats=[0,0,0,0]):
		self.direction = False
		self.last_direction = False
		self.head = [round((grid_size[0]-.5)/2),round((grid_size[1]-.5)/2)]
		self.body = []
		self.objective = []
		self.move_acc = 0.0
		self.can_move = True
		self.paused = False
		self.dying = False
		self.max_length = 1
		self.speed = speed
		[self.loop_screen,self.immortal,self.god_mode,self.manual_move] = cheats
	def generateObjective(self):
		self.objective = []
		while self.objective == []:
			potential = [randint(0,grid_size[0]-1),randint(0,grid_size[1]-1)]
			if potential not in self.body:
				self.objective = potential
				return self.objective
	def move(self,td=1,direction=False): ## Here is the most complex snake function.

		## DeltaTime accountant.
		if self.move_acc >= 1/[self.speed,5][self.manual_move]:
			self.move_acc = 0.0
			self.can_move = True
		else:
			self.move_acc += td

		## Change directions/pause the game.
		if direction:
			if direction == "pause":
				if self.paused: self.direction = self.last_direction
				self.paused = [True,False][self.paused]
			elif self.max_length==1 or self.god_mode or self.direction != {"up":"down","down":"up","left":"right","right":"left"}[direction]:
				self.direction = direction
				if self.paused: self.paused = False
			return()

		## Moves in accordance with the movement timer, as long as the death animation isn't playing.
		if self.can_move and not self.dying:

			## Sets where the snake is moving next.
			if self.direction in deltas:
				delta = deltas[self.direction]
				## Complex nesting is calculating what the snake's new head will be once it moves, along with any modifications due to cheats.
				new_head = [[[[grid_size[xy]-1,0][self.head[xy]+delta[xy]<=0],[self.head[xy]+delta[xy],[0,grid_size[xy]-1][self.head[xy]+delta[xy]==-1]][self.head[xy]+delta[xy] in [-1,grid_size[xy]]]][self.loop_screen],self.head[xy]+delta[xy]][0<self.head[xy]+delta[xy]<grid_size[xy]-1] for xy in range(2)]

				if new_head in self.body and not self.god_mode:
					return(self.die())
				else: self.head = new_head
			else:
				return()

			## Making sure we know what happens next with the snake.
			self.last_direction = self.direction
			self.can_move = False
			self.body.append(self.head)

			## Interaction with the snake's objective.
			if not self.objective:
				return([self.head,self.generateObjective(),self.body.pop(0)])
			elif self.head == self.objective:
				self.max_length += 1
				if self.max_length == grid_size[0]*grid_size[1]//2*2:
					return([self.objective])
				else:
					return([self.head,self.generateObjective()])
			else:
				return([self.head,self.body.pop(0)])

		## Loops the dying animation.
		elif self.dying:
			return(self.die())

		## Used if the snake isn't ready to move based on the time accountant.	
		else: return()
	def die(self,force=False):
		## Complex nesting is calculating if it's possible to move in any direction at all.
		if not force and not self.dying and self.immortal and True in [[[[[grid_size[xy]-1,0][self.head[xy]+deltas[delta][xy]<=0],[self.head[xy]+deltas[delta][xy],[0,grid_size[xy]-1][self.head[xy]+deltas[delta][xy]==-1]][self.head[xy]+deltas[delta][xy] in [-1,grid_size[xy]]]][self.loop_screen],self.head[xy]+deltas[delta][xy]][0<self.head[xy]+deltas[delta][xy]<grid_size[xy]-1] for xy in range(2)] not in self.body for delta in deltas]:
			return()
		else:
			## Playing the death animation.
			if len(self.body) > 0:
				if not self.dying:
					self.dying = True
				return([self.body.pop()])
			else:
				self.direction = False
				return([self.objective])

## Compiling Objects

class Game:
	def __init__(self):
		self.screen = False
		self.window = WindowObj()
		self.start_text =			TextObj(self.window.size,"MOVE TO START",			fg_color,		-grid_size[1]*box_size/6*2,				is_bold=True)
		self.win_text =				TextObj(self.window.size,"Y O U   W I N",			bg_color,		-grid_size[1]*box_size/6*2,				is_bold=True)
		self.lose_text =			TextObj(self.window.size,"Y O U   L O S E",			fg_color,		-grid_size[1]*box_size/6*2,				is_bold=True)
		self.changesettings_text =	TextObj(self.window.size,"SETTINGS",				fg_color_2,		-grid_size[1]*box_size/6*1.5,							relative_font_size=0.75)
		self.score_text =			TextObj(self.window.size,"SCORE: ",									y_offset=-grid_size[1]*box_size/6*1,	is_bold=True,	string_additions=[" "])
		self.highscore_text =		TextObj(self.window.size,"HIGHEST SCORE: ",							y_offset=-grid_size[1]*box_size/6*.5,					string_additions=[" "])
		self.newhighscore_text =	TextObj(self.window.size,"NEW HIGH-SCORE!",			sp_color,												is_bold=True,	relative_font_size=2/3)
		self.woah_text =			TextObj(self.window.size,"(I bet that was hard!)",	sp_color,												is_bold=True,	relative_font_size=2/3)
		self.pause_text =			TextObj(self.window.size,"P A U S E D",				sp_color,												is_bold=True)
		self.restart_text =			TextObj(self.window.size,"(PRESS ENTER TO RESTART)",sp_color,		y_offset=grid_size[1]*box_size/6*2.5,					relative_font_size=2/3)
		self.end_text =				TextObj(self.window.size,"ENTER TO RESTART",						y_offset=grid_size[1]*box_size/6*1)
		self.exit_text =			TextObj(self.window.size,"ESC TO EXIT",								y_offset=grid_size[1]*box_size/6*2)
		self.enablecheats_text =	TextObj(self.window.size,"ENABLE CHEATS",							y_offset=grid_size[1]*box_size/6*1) #,					relative_font_size=0.5)
		self.settings_text =		TextObj(self.window.size,"S E T T I N G S",			fg_color,		-grid_size[1]*box_size/6*2,				is_bold=True)
		self.speed_text =			TextObj(self.window.size,"SPEED",					fg_color,		-grid_size[1]*box_size/6*1)
		self.speedvalue_text =		TextObj(self.window.size,"",						fg_color,		-grid_size[1]*box_size/6*.25,			is_bold=True,	string_additions=[" "],relative_font_size=2)
		self.speedarrowl_text =		TextObj(self.window.size,"<     ",					fg_color,		-grid_size[1]*box_size/6*.25,			is_bold=True,	relative_font_size=2,	x_alignment="l")
		self.speedarrowr_text =		TextObj(self.window.size,"     >",					fg_color,		-grid_size[1]*box_size/6*.25,			is_bold=True,	relative_font_size=2,	x_alignment="r")
		self.savecheats_text =		TextObj(self.window.size,"SAVE CHEAT SCORES",		fg_color,		grid_size[1]*box_size/6*.5)
		self.back_text =			TextObj(self.window.size,"GO BACK",					fg_color_2,		grid_size[1]*box_size/6*2)
		self.cheats_text =			TextObj(self.window.size,"C H E A T S",								y_offset=-grid_size[1]*box_size/6*2,	is_bold=True)
		self.loop_text =			TextObj(self.window.size,"LOOP SCREEN",								y_offset=-grid_size[1]*box_size/6*1)
		self.immortal_text =		TextObj(self.window.size,"IMMORTAL")
		self.godmode_text =			TextObj(self.window.size,"GOD MODE",								y_offset=grid_size[1]*box_size/6*1)
		self.highscore = 0
		self.new_highscore = 0
		self.save_cheat_scores = save_cheat_scores
		self.loop_screen = loop_screen
		self.immortal = immortal
		self.god_mode = god_mode
		self.manual_move = manual_move
		self.speed = speed
		self.start()
	def start(self):	## Setting things up to play again.
		self.paused = False
		self.grid = [[GridObj([x,y]) for y in range(grid_size[1])] for x in range(grid_size[0])]
		self.snake = SnakeObj(self.speed,[self.loop_screen,self.immortal,self.god_mode,self.manual_move])
		# pygame.draw.rect(self.window.surface,bg_color,play_rect)
		self.snake.body.append(self.grid[self.snake.head[0]][self.snake.head[1]].switch(self.window.surface))
		self.start_time = 0.0
	def update(self,box_list=[],mouse_xy=False):	## This is another complex function because it manages the screens as well.
		self.time_delta = fps.tick(30)/1000.0	## DeltaTime ticker.

		if self.snake.direction and not (self.snake.paused or self.paused):	## Only this one controls what happens during the actual game.
			if self.screen != "play":
				self.screen = "play"
				pygame.draw.rect(self.window.surface,bg_color,play_rect)
			if not box_list:
				for boxID in self.snake.move([self.time_delta,0][self.manual_move]):
					self.grid[boxID[0]][boxID[1]].switch(self.window.surface,custom_color=[False,sp_color][boxID == self.snake.objective and self.snake.head != self.snake.objective])
			else:
				done_boxes = []
				for boxID in box_list:
					self.grid[boxID[0]][boxID[1]].switch(self.window.surface,swap_colors=[False,True][boxID in done_boxes],custom_color=[[fg_color,False][boxID in done_boxes],sp_color][boxID == self.snake.objective and self.snake.head != self.snake.objective])
					done_boxes.append(boxID)
			if self.snake.max_length == grid_size[0]*grid_size[1]//2*2:
				self.snake.direction = False
				self.update()
		else:
			## This stuff all happens outside of the game. (Eg. stats, menues, etc.)
			if self.snake.paused or self.paused: ## Pause overlay.
				if self.screen != "pause":
					self.screen = "pause"
					self.direction = False
					self.paused = True
					self.pause_text.draw(self.window.surface)
					self.restart_text.draw(self.window.surface)
				else:
					if not self.snake.paused:
						self.paused = False
						self.update(self.snake.body+[self.snake.objective])
			elif self.snake.max_length == grid_size[0]*grid_size[1]//2*2 and self.screen in ["play","lose"]:	## Win screen.
					self.screen = "win"
					woah = False
					pygame.draw.rect(self.window.surface,fg_color,play_rect)
					self.win_text.draw(self.window.surface)
					self.score_text.draw(self.window.surface,bg_color,string_additions=[str(self.snake.max_length)])
					self.highscore_text.draw(self.window.surface,bg_color,string_additions=[str(self.highscore)])
					self.end_text.draw(self.window.surface,[fg_color_2,fg_color][self.end_text.text_rect.collidepoint(pygame.mouse.get_pos())])
					self.exit_text.draw(self.window.surface,[fg_color_2,fg_color][self.exit_text.text_rect.collidepoint(pygame.mouse.get_pos())])
					if grid_size[0]*grid_size[1]//2*2 != grid_size[0]*grid_size[1] and not self.cheats_enabled:
						self.woah_text.draw(self.window.surface)
						woah = True
					if self.snake.max_length > self.highscore:
						if not self.cheats_enabled or (self.cheats_enabled and self.save_cheat_scores):
							if not woah: self.newhighscore_text.draw(self.window.surface)
							self.new_highscore = self.snake.max_length
					if mouse_xy:
						if mouse_xy[1] == 1:
							if self.end_text.text_rect.collidepoint(mouse_xy[0]): self.screen = "start";self.start()
							if self.exit_text.text_rect.collidepoint(mouse_xy[0]): pygame.quit();exit()
			elif self.snake.dying and self.screen in ["play","lose"]:	## Death screen.
					self.screen = "lose"
					pygame.draw.rect(self.window.surface,bg_color,play_rect)
					self.lose_text.draw(self.window.surface)
					self.score_text.draw(self.window.surface,fg_color,string_additions=[str(self.snake.max_length),"/",str(grid_size[0]*grid_size[1]//2*2)])
					self.highscore_text.draw(self.window.surface,fg_color,string_additions=[str(self.highscore)])
					self.end_text.draw(self.window.surface,[fg_color_2,fg_color][self.end_text.text_rect.collidepoint(pygame.mouse.get_pos())])
					self.exit_text.draw(self.window.surface,[fg_color_2,fg_color][self.exit_text.text_rect.collidepoint(pygame.mouse.get_pos())])
					if self.snake.max_length > self.highscore:
						if not self.cheats_enabled or (self.cheats_enabled and self.save_cheat_scores):
							self.new_highscore = self.snake.max_length
							self.newhighscore_text.draw(self.window.surface)
					if mouse_xy:
						if mouse_xy[1] == 1:
							if self.end_text.text_rect.collidepoint(mouse_xy[0]): self.screen = "start";self.start()
							if self.exit_text.text_rect.collidepoint(mouse_xy[0]): pygame.quit();exit()
			else:
				if self.screen == "settings":	## Settings menu.
					pygame.draw.rect(self.window.surface,bg_color,play_rect)
					self.settings_text.draw(self.window.surface)
					self.speed_text.draw(self.window.surface,fg_color)
					self.speedarrowl_text.draw(self.window.surface,[fg_color_2,fg_color][self.speedarrowl_text.text_rect.collidepoint(pygame.mouse.get_pos())])
					self.speedarrowr_text.draw(self.window.surface,[fg_color_2,fg_color][self.speedarrowr_text.text_rect.collidepoint(pygame.mouse.get_pos())])
					self.speedvalue_text.draw(self.window.surface,fg_color,string_additions=[str(self.speed)])
					self.back_text.draw(self.window.surface,[fg_color_2,fg_color][self.back_text.text_rect.collidepoint(pygame.mouse.get_pos())])
					self.savecheats_text.draw(self.window.surface,[[fg_color_2,fg_color][self.savecheats_text.text_rect.collidepoint(pygame.mouse.get_pos())],sp_color][self.save_cheat_scores])
					self.enablecheats_text.draw(self.window.surface,[fg_color_2,sp_color][self.enablecheats_text.text_rect.collidepoint(pygame.mouse.get_pos())])
					if mouse_xy:
						if mouse_xy[1] == 1:
							if self.speedarrowl_text.text_rect.collidepoint(mouse_xy[0]) and self.speed > 0.0: self.speed -= 0.5
							if self.speedarrowr_text.text_rect.collidepoint(mouse_xy[0]) and self.speed < 10.0: self.speed += 0.5
							if self.savecheats_text.text_rect.collidepoint(mouse_xy[0]): self.save_cheat_scores = [True,False][self.save_cheat_scores]
							if self.back_text.text_rect.collidepoint(mouse_xy[0]): self.screen = "start"
							if self.enablecheats_text.text_rect.collidepoint(mouse_xy[0]): self.screen = "cheats"
						elif mouse_xy[1] in [4,6,8,10]:
							if self.speedvalue_text.text_rect.collidepoint(mouse_xy[0]) and self.speed < 10.0: self.speed += 0.5
						elif mouse_xy[1] in [5,7,9,11]:
							if self.speedvalue_text.text_rect.collidepoint(mouse_xy[0]) and self.speed > 0.0: self.speed -= 0.5
						self.snake.speed = self.speed

				elif self.screen == "cheats":	## Cheats menu.
					pygame.draw.rect(self.window.surface,bg_color,play_rect)
					self.cheats_text.draw(self.window.surface)
					self.loop_text.draw(self.window.surface,[[fg_color_2,fg_color][self.loop_text.text_rect.collidepoint(pygame.mouse.get_pos())],sp_color][self.loop_screen])
					self.immortal_text.draw(self.window.surface,[[fg_color_2,fg_color][self.immortal_text.text_rect.collidepoint(pygame.mouse.get_pos())],sp_color][self.immortal])
					self.godmode_text.draw(self.window.surface,[[fg_color_2,fg_color][self.godmode_text.text_rect.collidepoint(pygame.mouse.get_pos())],sp_color][self.god_mode])
					self.back_text.draw(self.window.surface,[fg_color_2,fg_color][self.back_text.text_rect.collidepoint(pygame.mouse.get_pos())])
					if mouse_xy:
						if mouse_xy[1] == 1:
							if self.loop_text.text_rect.collidepoint(mouse_xy[0]):
								self.loop_screen = self.snake.loop_screen = [True,False][self.loop_screen]
								if not self.snake.loop_screen and self.snake.god_mode: self.god_mode = self.snake.god_mode = False
							elif self.immortal_text.text_rect.collidepoint(mouse_xy[0]):
								self.immortal = self.snake.immortal = [True,False][self.immortal]
								if not self.snake.immortal and self.snake.god_mode: self.god_mode = self.snake.god_mode = False
							elif self.godmode_text.text_rect.collidepoint(mouse_xy[0]):
								self.god_mode = self.snake.god_mode = self.loop_screen = self.snake.loop_screen = self.immortal = self.snake.immortal = [True,False][self.god_mode]
							elif self.back_text.text_rect.collidepoint(mouse_xy[0]):
								self.screen = "settings"
				else:
					self.screen = "start"	## Start menu.
					self.highscore = self.new_highscore
					self.cheats_enabled = True in [self.snake.loop_screen,self.snake.immortal,self.snake.god_mode,self.snake.manual_move]
					if not self.snake.speed:
						self.manual_move = self.snake.manual_move = True
					else: self.manual_move = False
					pygame.draw.rect(self.window.surface,bg_color,play_rect)
					self.grid[self.snake.head[0]][self.snake.head[1]].draw(self.window.surface)
					self.start_text.draw(self.window.surface)
					self.changesettings_text.draw(self.window.surface,[fg_color_2,fg_color][self.changesettings_text.text_rect.collidepoint(pygame.mouse.get_pos())])
					self.exit_text.draw(self.window.surface,[fg_color_2,fg_color][self.exit_text.text_rect.collidepoint(pygame.mouse.get_pos())])
					if mouse_xy:
						if mouse_xy[1] == 1:
							if self.changesettings_text.text_rect.collidepoint(mouse_xy[0]): self.screen = "settings"
							if self.exit_text.text_rect.collidepoint(mouse_xy[0]):
								pygame.quit();exit()

		pygame.display.flip()

## Initializing Main Game

if god_mode: loop_screen = immortal = True

if fullscreen:
	infoObject = pygame.display.Info()
	grid_size = [infoObject.current_w//box_size,infoObject.current_h//box_size]
	display_offset = [infoObject.current_w-box_size*grid_size[0],infoObject.current_h-box_size*grid_size[1]]
	play_rect = pygame.Rect([offset//2 for offset in display_offset],[grid_size[xy]*box_size for xy in range(2)])
else: play_rect = pygame.Rect([0,0],[grid_size[xy]*box_size for xy in range(2)])

game = Game()
pygame.event.set_blocked(None)
pygame.event.set_allowed([pygame.MOUSEBUTTONDOWN,pygame.KEYDOWN,pygame.KEYUP,pygame.QUIT,pygame.MOUSEWHEEL])
run = True

## Main Loop

while run:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		elif event.type == pygame.MOUSEBUTTONDOWN:
			game.update(mouse_xy=[pygame.mouse.get_pos(),event.button])				## Mouse actions.
		elif event.type == pygame.KEYDOWN:											## Movement keys, including hold-down function.
			if event.key in direction_keys:
				game.snake.move(speed,direction_keys[event.key])
				fps.tick(15)	## Extra delay to promote controllability.
				pressed_keys = [event.key]
				while pressed_keys and not game.snake.dying:
					game.update(game.snake.move(game.time_delta*[1,2][game.manual_move],direction_keys[pressed_keys[-1]]))
					for loop_event in pygame.event.get():
						if loop_event.type == pygame.KEYUP:
							pressed_keys.remove(loop_event.key)
						elif loop_event.type == pygame.KEYDOWN and loop_event.key in direction_keys:
							pressed_keys.append(loop_event.key)
			elif event.key == pygame.K_SPACE and game.screen in ["play","pause"]:	## Pause.
				game.snake.move(direction="pause")
			elif event.key == pygame.K_ESCAPE:										## Exit.
				if game.screen == "settings": game.screen = "start"
				elif game.screen == "cheats": game.screen = "settings"
				else: run = False
			elif event.key == pygame.K_RETURN and game.screen in ["win","lose","pause"]:
				game.start()

			## Debug Buttons

			# elif event.key == pygame.K_e and game.screen in ["play","pause"]: 		## Lose on purpose.
			# 	game.snake.die(True)
			# elif event.key == pygame.K_q and game.screen in ["play","pause"]: 		## Jump between objectives.
			# 	if not game.manual_move:
			# 		q_loop = True
			# 		while len(game.snake.body) != grid_size[0]*grid_size[1]//2*2 and q_loop:
			# 			game.snake.head = [[game.snake.objective[xy]-deltas[game.snake.direction][xy] for xy in range(2)],game.snake.objective][game.manual_move]
			# 			game.update()
			# 			for loop_event in pygame.event.get():
			# 				if loop_event.type == pygame.KEYDOWN and loop_event.key in [pygame.K_SPACE,pygame.K_ESCAPE,pygame.K_q]:
			# 					q_loop = False
			# 					if event.key == pygame.K_SPACE and game.screen in ["play","pause"]:
			# 						game.snake.move(direction="pause")
			# 					elif event.key == pygame.K_ESCAPE:
			# 						run = False
			# 	else: game.snake.head = game.snake.objective

	game.update()	## Automatic snake.move() and display.flip() included inside this function.

## Exit Protocols

pygame.quit()
exit()
