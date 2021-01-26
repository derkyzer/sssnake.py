
import pygame
from random import randint

pygame.init()
fps = pygame.time.Clock()		# Adjust text to go by x or y, whichever is smaller.

## Default Launch Settings

grid_size = [7,10]			## To make the start screen more beautiful, make this a [odd number,even number].
box_size = 75				## 50-100 recommended.
speed = 4					## 3.5 - 4.5 recommended for 10x10. Maybe set higher for large grids.

loop_screen = False			## Loops the sides of the screens. You can still die by colliding with the snake's body.
manual_move = False			## Snake doesn't move automatically unless the button is held down.

god_mode = False 			## Immortal, screen loops, and pass through snake body.
immortal = False 			## Can't die, just stops the snake. You can still die the snake gets stuck.
save_cheat_scores = False	## Scores will save while cheats are enabled.

bg_color = "gray12"
fg_color = "gray96"
fg_color_2 = "gray77"
sp_color = "firebrick"

font_name = "calibri"		## Some standard fonts might be: calibri, verdana, arial, trebuchetms, candara, corbel...

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

class WindowObj: ## Could implement menus here to change in-game settings like cheats.
	def __init__(self):
		self.color = bg_color
		self.size = [box_size*grid_wh for grid_wh in grid_size]
		self.surface = pygame.display.set_mode(self.size,vsync=0)
		pygame.display.set_caption('SSSNAKE.py')

class GridObj:
	def __init__(self,box_id):
		self.color = bg_color
		self.swap_pallette = {fg_color:bg_color,bg_color:fg_color,sp_color:fg_color}
		self.box_id = box_id
	def draw(self,surface):
		pygame.draw.rect(surface,self.color,[[box_size*box_xy for box_xy in self.box_id],[box_size,box_size]])
	def switch(self,surface,swap_colors=True,custom_color=False):
		self.color = [custom_color,[self.color,self.swap_pallette[self.color]][swap_colors]][not custom_color]
		self.draw(surface)
		return(self.box_id)

class TextObj:
	def __init__(self,window_size,string,color=fg_color,y_offset=0,string_additions=[],is_bold=False,relative_font_size=1):
		self.base_string = string
		self.color = color
		try: self.font = pygame.font.SysFont(font_name,round((grid_size[0]*box_size*relative_font_size)/10),bold=is_bold)
		except: self.font = pygame.font.SysFont("default",round((grid_size[0]*box_size*relative_font_size)/10),bold=is_bold)
		self.window_size = window_size
		self.y_offset = y_offset
		self.enabled = False
		if not string_additions:
			self.string = self.base_string
			self.text = self.font.render(self.string,True,self.color)
			self.text_rect = self.text.get_rect(center=(self.window_size[0]/2,self.window_size[1]/2+self.y_offset))
	def draw(self,surface,change_color=False,string_additions=[],y_offset=0):
		if y_offset:
			self.y_offset = y_offset
			self.text_rect = self.text.get_rect(center=(self.window_size[0]/2,self.window_size[1]/2+self.y_offset))
		if string_additions:
			self.string = self.base_string + " ".join(string_additions)
			self.text = self.font.render(self.string,True,self.color)
			self.text_rect = self.text.get_rect(center=(self.window_size[0]/2,self.window_size[1]/2+self.y_offset))
		if change_color:
			self.color = change_color
			self.text = self.font.render(self.string,True,self.color)
		surface.blit(self.text,self.text_rect)

class SnakeObj:
	def __init__(self):
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
	def generateObjective(self):
		self.objective = []
		while self.objective == []:
			potential = [randint(0,grid_size[0]-1),randint(0,grid_size[1]-1)]
			if potential not in self.body:
				self.objective = potential
				return self.objective
	def move(self,td=speed,direction=False): ## Probably the most complex function.

		## Movement timer.
		if self.move_acc >= 1/speed:
			self.move_acc = 0.0
			self.can_move = True
		else:
			self.move_acc += td

		## Change directions/pause the game.
		if direction:
			if direction == "pause":
				if self.paused: self.direction = self.last_direction
				self.paused = [True,False][self.paused]
			elif direction in deltas and self.max_length==1 or self.god_mode or self.direction != {"up":"down","down":"up","left":"right","right":"left"}[direction]:
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

				if new_head in self.body and not self.god_mode: return(self.die())
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
	def __init__(self):	## This stuff is mostly dynamically updated.
		self.screen = False
		self.window = WindowObj()
		self.start_text = TextObj(self.window.size,"MOVE TO START",fg_color,-grid_size[1]*box_size/6*2,is_bold=True)
		self.win_text = TextObj(self.window.size,"Y O U   W I N",bg_color,-grid_size[1]*box_size/6*2,is_bold=True)
		self.lose_text = TextObj(self.window.size,"Y O U   L O S E",fg_color,-grid_size[1]*box_size/6*2,is_bold=True)
		self.score_text = TextObj(self.window.size,"SCORE: ",y_offset=-grid_size[1]*box_size/6*1,string_additions=[" "],is_bold=True)
		self.highscore_text = TextObj(self.window.size,"HIGHEST SCORE: ",y_offset=-grid_size[1]*box_size/6*.5,string_additions=[" "])
		self.woah_text = TextObj(self.window.size,"(I bet that was hard!)",sp_color,0,is_bold=True,relative_font_size=2/3)
		self.pause_text = TextObj(self.window.size,"P A U S E D",sp_color,0,is_bold=True)
		self.end_text = TextObj(self.window.size,"ENTER TO RESTART",y_offset=grid_size[1]*box_size/6*1)
		self.exit_text = TextObj(self.window.size,"ESC TO EXIT",y_offset=grid_size[1]*box_size/6*2)
		self.enablecheats_text = TextObj(self.window.size,"ENABLE CHEATS",y_offset=grid_size[1]*box_size/6*2.5,relative_font_size=0.5)
		self.cheats_text = TextObj(self.window.size,"C H E A T S",y_offset=-grid_size[1]*box_size/6*2,is_bold=True)
		self.loop_text = TextObj(self.window.size,"LOOP SCREEN",y_offset=-grid_size[1]*box_size/6*1)
		self.immortal_text = TextObj(self.window.size,"IMMORTAL")
		self.godmode_text = TextObj(self.window.size,"GOD MODE",y_offset=grid_size[1]*box_size/6*1)
		self.back_text = TextObj(self.window.size,"GO BACK",y_offset=grid_size[1]*box_size/6*2.5)
		self.highscore = 0
		self.loop_screen = loop_screen
		self.immortal = immortal
		self.god_mode = god_mode
		self.start()
	def start(self):	## Setting things up to play again.
		self.paused = False
		self.grid = [[GridObj([x,y]) for y in range(grid_size[1])] for x in range(grid_size[0])]
		self.snake = SnakeObj()
		self.window.surface.fill(bg_color)
		self.snake.body.append(self.grid[self.snake.head[0]][self.snake.head[1]].switch(self.window.surface))
		self.start_time = 0.0
	def update(self,box_list=[],mouse_xy=False):
		self.time_delta = fps.tick(30)/1000.0

		if self.snake.direction and not (self.snake.paused or self.paused):	## What happens during the actual game.
			if self.screen != "play":
				self.screen = "play"
				self.snake.loop_screen = self.loop_screen
				self.snake.immortal = self.immortal
				self.snake.god_mode = self.god_mode
				self.window.surface.fill(bg_color)
			if not box_list:
				for boxID in self.snake.move([self.time_delta,0][manual_move]):
					self.grid[boxID[0]][boxID[1]].switch(self.window.surface,custom_color=[False,sp_color][boxID == self.snake.objective and self.snake.head != self.snake.objective])
			else:
				done_boxes = []
				for boxID in box_list:
					self.grid[boxID[0]][boxID[1]].switch(self.window.surface,swap_colors=[False,True][boxID in done_boxes],custom_color=[[fg_color,False][boxID in done_boxes],sp_color][boxID == self.snake.objective and self.snake.head != self.snake.objective])
					done_boxes.append(boxID)
			if self.snake.max_length == grid_size[0]*grid_size[1]//2*2:
				self.snake.direction = False
				self.update()
		else:	## Stuff that happens outside of the game. (Eg. stats, menues, etc.)
			if self.snake.paused or self.paused:
				if self.screen != "pause":	## Only displaying it once so the screen isn't being constantly redrawn.
					self.screen = "pause"
					self.direction = False
					self.paused = True
					self.pause_text.draw(self.window.surface)
				else:
					if not self.snake.paused:
						self.paused = False
						self.update(self.snake.body+[self.snake.objective])
			elif self.snake.max_length == grid_size[0]*grid_size[1]//2*2:
				if self.screen != "win":	## Only displaying it once so the screen isn't being constantly redrawn.
					self.screen = "win"
					self.window.surface.fill(fg_color)
					self.win_text.draw(self.window.surface)
					self.score_text.draw(self.window.surface,bg_color,string_additions=[str(self.snake.max_length)])
					self.highscore_text.draw(self.window.surface,bg_color,string_additions=[str(self.highscore)])
					if grid_size[0]*grid_size[1]//2*2 != grid_size[0]*grid_size[1] and not cheats_enabled: self.woah_text.draw(self.window.surface)
					self.end_text.draw(self.window.surface,bg_color)
					self.exit_text.draw(self.window.surface,bg_color)
					if self.snake.max_length > self.highscore:
						if not cheats_enabled or (cheats_enabled and save_cheat_scores):
							if self.snake.max_length > self.highscore: self.highscore = self.snake.max_length
			elif self.snake.dying:
				if self.screen != "lose":	## Only displaying it once so the screen isn't being constantly redrawn.
					self.screen = "lose"
					self.window.surface.fill(bg_color)
					self.lose_text.draw(self.window.surface)
					self.score_text.draw(self.window.surface,fg_color,string_additions=[str(self.snake.max_length),"/",str(grid_size[0]*grid_size[1]//2*2)])
					self.highscore_text.draw(self.window.surface,fg_color,string_additions=[str(self.highscore)])
					self.end_text.draw(self.window.surface,fg_color)
					self.exit_text.draw(self.window.surface,fg_color)
					if self.snake.max_length > self.highscore:
						if not cheats_enabled or save_cheat_scores:
							if self.snake.max_length > self.highscore: self.highscore = self.snake.max_length
			else:
				if self.screen != "cheats":
					self.screen = "start"
					self.window.surface.fill(bg_color)
					self.grid[self.snake.head[0]][self.snake.head[1]].draw(self.window.surface)
					self.start_text.draw(self.window.surface)
					self.exit_text.draw(self.window.surface,fg_color)
					self.enablecheats_text.draw(self.window.surface,[sp_color,fg_color][self.enablecheats_text.text_rect.collidepoint(pygame.mouse.get_pos())])
					if mouse_xy:
						if self.enablecheats_text.text_rect.collidepoint(mouse_xy): self.screen = "cheats"
				else:
					self.window.surface.fill(bg_color)
					self.cheats_text.draw(self.window.surface)
					self.loop_text.draw(self.window.surface,[[fg_color_2,fg_color][self.loop_text.text_rect.collidepoint(pygame.mouse.get_pos())],sp_color][self.loop_screen])
					self.immortal_text.draw(self.window.surface,[[fg_color_2,fg_color][self.immortal_text.text_rect.collidepoint(pygame.mouse.get_pos())],sp_color][self.immortal])
					self.godmode_text.draw(self.window.surface,[[fg_color_2,fg_color][self.godmode_text.text_rect.collidepoint(pygame.mouse.get_pos())],sp_color][self.god_mode])
					self.back_text.draw(self.window.surface,[fg_color_2,fg_color][self.back_text.text_rect.collidepoint(pygame.mouse.get_pos())])

					if mouse_xy: ## Basic clickables in menues. These variabels pass into the snake object when play starts.
						for text_object in [self.loop_text,self.immortal_text,self.godmode_text,self.back_text]:
							if text_object.text_rect.collidepoint(mouse_xy):
								if text_object == self.loop_text:
									self.loop_screen = [True,False][self.loop_screen]
									if not self.loop_screen and self.god_mode: self.god_mode = False
								elif text_object == self.immortal_text:
									self.immortal = [True,False][self.immortal]
									if not self.immortal and self.god_mode: self.god_mode = False
								elif text_object == self.godmode_text:
									self.god_mode = self.loop_screen = self.immortal = [True,False][self.god_mode]
								elif text_object == self.back_text:
									self.screen = "start"

		pygame.display.flip()

## Initializing Main Game

if god_mode: loop_screen = immortal = True
cheats_enabled = True in [god_mode,loop_screen,immortal]

game = Game()
pygame.event.set_blocked(None)
pygame.event.set_allowed([pygame.MOUSEBUTTONDOWN,pygame.KEYDOWN,pygame.KEYUP,pygame.QUIT])
run = True

## Main Loop

while run:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
			# print(pygame.mouse.get_pressed()[0])
			game.update(mouse_xy=pygame.mouse.get_pos())
		elif event.type == pygame.KEYDOWN:											## Movement keys, including hold-down function.
			if event.key in direction_keys:
				game.snake.move(speed,direction_keys[event.key])
				pressed_keys = [event.key]
				while pressed_keys:
					game.snake.move(game.time_delta*[1,2][manual_move],direction_keys[pressed_keys[-1]])
					game.update()
					for loop_event in pygame.event.get():
						if loop_event.type == pygame.KEYUP:
							pressed_keys.remove(loop_event.key)
						elif loop_event.type == pygame.KEYDOWN and loop_event.key in direction_keys:
							pressed_keys.append(loop_event.key)
			elif event.key == pygame.K_SPACE and game.screen in ["play","pause"]:	## Pause.
				game.snake.move(direction="pause")
			elif event.key == pygame.K_ESCAPE:										## Exit.
				run = False
			elif event.key == pygame.K_RETURN and game.screen in ["win","lose"]:	## Restart.
				game.start()

			## Debug Buttons

			# elif event.key == pygame.K_e and game.screen in ["play","pause"]: 		## Lose on purpose.
			# 	game.snake.die(True)
			# elif event.key == pygame.K_q and game.screen in ["play","pause"]: 		## Jump between objectives.
			# 	if not manual_move:
			# 		q_loop = True
			# 		while len(game.snake.body) != grid_size[0]*grid_size[1]//2*2 and q_loop:
			# 			game.snake.head = [[game.snake.objective[xy]-deltas[game.snake.direction][xy] for xy in range(2)],game.snake.objective][manual_move]
			# 			game.update()
			# 			for loop_event in pygame.event.get():
			# 				if loop_event.type == pygame.KEYDOWN and loop_event.key in [pygame.K_SPACE,pygame.K_ESCAPE,pygame.K_q]:
			# 					q_loop = False
			# 					if event.key == pygame.K_SPACE and game.screen in ["play","pause"]:
			# 						game.snake.move(direction="pause")
			# 					elif event.key == pygame.K_ESCAPE:
			# 						run = False
			# 	else: game.snake.head = game.snake.objective

	game.update()	## display.flip() included inside this function.

## Exit Protocols

pygame.quit()
exit()
