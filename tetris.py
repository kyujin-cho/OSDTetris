'''
Copyright (c) 2010 "Laria Carolin Chabowski"<me@laria.me>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

from random import randrange as rand
import pygame #!
import os.path
import json
from tinydb import TinyDB #!
import time
import math
import requests #!
import sys

# The configuration
cell_size =	18
cols =		10
rows =		22
maxfps = 	30

colors = [
(0,   0,   0  ),
(255, 85,  85),
(120, 108, 245),
(100, 200, 115),
(146, 202, 73 ),
(255, 140, 50 ),
(50,  120, 52 ),
(150, 161, 218 ),
(35,  35,  35) # Helper color for background grid
]

# Define the shapes of the single parts
tetris_shapes = [
	[[1, 1, 1],
	 [0, 1, 0]],
	
	[[0, 2, 2],
	 [2, 2, 0]],
	
	[[3, 3, 0],
	 [0, 3, 3]],
	
	[[4, 0, 0],
	 [4, 4, 4]],
	
	[[0, 0, 5],
	 [5, 5, 5]],
	
	[[6, 6, 6, 6]],
	
	[[7, 7],
	 [7, 7]]
]

ip_addr = ''

def rotate_clockwise(shape):
	return [ [ shape[y][x]
			for y in iter(range(len(shape))) ]
		for x in iter(range(len(shape[0]) - 1, -1, -1)) ]

def check_collision(board, shape, offset):
	off_x, off_y = offset
	for cy, row in enumerate(shape):
		for cx, cell in enumerate(row):
			try:
				if cell and board[ cy + off_y ][ cx + off_x ]:
					return True
			except IndexError:
				return True
	return False

def remove_row(board, row):
	del board[row]
	return [[0 for i in iter(range(cols))]] + board
	
def join_matrixes(mat1, mat2, mat2_off):
	off_x, off_y = mat2_off
	for cy, row in enumerate(mat2):
		for cx, val in enumerate(row):
			mat1[cy+off_y-1	][cx+off_x] += val
	return mat1

def new_board():
	board = [ [ 0 for x in iter(range(cols)) ]
			for y in iter(range(rows)) ]
	board += [[ 1 for x in iter(range(cols))]]
	return board

class TetrisApp(object):
	def __init__(self):
		pygame.init()
		pygame.key.set_repeat(250,25)
		self.width = cell_size*(cols+10)
		self.height = cell_size*rows
		self.rlim = cell_size*cols
		self.bground_grid = [[ 8 if x%2==y%2 else 0 for x in iter(range(cols))] for y in iter(range(rows))]
		pygame.font.init()
		self.default_font = pygame.font.Font('files/NanumGothic.ttf', 12)
		
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.event.set_blocked(pygame.MOUSEMOTION) # We do not need
		                                             # mouse movement
		                                             # events, so we
		                                             # block them.
		self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
		self.is_music_loaded = False
		self.is_music_playing = False
		# if os.path.isfile('data.json'):
		# 	self.usr_data = json.loads(open('data.json', 'r').read())
		# else:
		# 	self.usr_data = {'highest_score': 0, 'total_play': 0}
		self.db = TinyDB('files/data.ldb')
		self.init_game()

	def new_stone(self):
		self.already_restored = False
		self.stone = self.next_stone[:]
		self.next_stone = tetris_shapes[rand(len(tetris_shapes))]
		self.stone_x = int(cols / 2 - len(self.stone[0])/2)
		self.stone_y = 0
		
		if check_collision(self.board,
		                   self.stone,
		                   (self.stone_x, self.stone_y)):
			self.gameover = True
	
	def init_game(self):
		global ip_addr
		if ip_addr != '':
			pygame.display.set_caption('파이-테트리스(서버: ' + ip_addr + ')')
		else:
			pygame.display.set_caption('파이-테트리스 로-칼 모드')
		self.board = new_board()
		self.new_stone()
		self.level = 1
		self.score = 0
		self.lines = 0
		self.speed_level = 0
		self.already_restored = False
		self.restorable_block = None
		pygame.mixer.init()
		if os.path.isfile('files/bg_music.ogg'):
			pygame.mixer.music.load('files/bg_music.ogg')
			pygame.mixer.music.play()
			self.is_music_loaded = True
			self.is_music_playing = True
		pygame.time.set_timer(pygame.USEREVENT+1, 1000)
		self.start_time = time.time()
		self.high_score = -1
		# print(self.db.exists())
		# print(self.db.all())
		# if self.db.all() != None:
		if ip_addr == '':
			for item in iter(self.db):
				if item['score'] > self.high_score:
					self.high_score = item['score']
			if self.high_score is -1:
				self.high_score = 0
		else:
			response = requests.get('http://' + ip_addr + ':5000/scores/highest').json()
			if response['data'] is None:
				self.high_score = 0
				self.high_scorer = ''
			else:
				self.high_score = response['data']['score']
				self.high_scorer = response['data']['name']
			self.my_name = input('이름?')
	
	def disp_msg(self, msg, topleft):
		x,y = topleft
		for line in msg.splitlines():
			self.screen.blit(
				self.default_font.render(
					line,
					False,
					(255,255,255),
					(0,0,0)),
				(x,y))
			y+=14
	
	def center_msg(self, msg):
		for i, line in enumerate(msg.splitlines()):
			msg_image =  self.default_font.render(line, False,
				(255,255,255), (0,0,0))
		
			msgim_center_x, msgim_center_y = msg_image.get_size()
			msgim_center_x //= 2
			msgim_center_y //= 2
		
			self.screen.blit(msg_image, (
			  self.width // 2-msgim_center_x,
			  self.height // 2-msgim_center_y+i*22))
	
	def draw_matrix(self, matrix, offset):
		off_x, off_y  = offset
		for y, row in enumerate(matrix):
			for x, val in enumerate(row):
				if val:
					pygame.draw.rect(
						self.screen,
						colors[val],
						pygame.Rect(
							(off_x+x) *
							  cell_size,
							(off_y+y) *
							  cell_size, 
							cell_size,
							cell_size),0)
	
	def add_cl_lines(self, n):
		linescores = [0, 40, 100, 300, 1200]
		self.lines += n
		self.score += linescores[n] * self.level
		if self.lines >= self.level*6:
			self.level += 1
			newdelay = 1000-50*(self.speed_level+self.level-1)
			newdelay = 100 if newdelay < 100 else newdelay
			pygame.time.set_timer(pygame.USEREVENT+1, newdelay)
	
	def move(self, delta_x):
		if not self.gameover and not self.paused:
			new_x = self.stone_x + delta_x
			if new_x < 0:
				new_x = 0
			if new_x > cols - len(self.stone[0]):
				new_x = cols - len(self.stone[0])
			if not check_collision(self.board,
			                       self.stone,
			                       (new_x, self.stone_y)):
				self.stone_x = new_x
	def quit(self):
		global ip_addr
		self.center_msg("종료 중...")
		pygame.display.update()
		if ip_addr == '':
			self.db.insert({'score' : self.score, 'level': self.level, 'time': time.time() - self.start_time})
		else:
			requests.post('http://' + ip_addr + ':5000/scores', data={'score' : self.score, 'level': self.level, 'time': time.time() - self.start_time, 'name': self.my_name})
		sys.exit()
	
	def drop(self, manual):
		if not self.gameover and not self.paused:
			# self.score += 1 if manual else 0
			self.stone_y += 1
			if check_collision(self.board,
			                   self.stone,
			                   (self.stone_x, self.stone_y)):
				self.board = join_matrixes(
				  self.board,
				  self.stone,
				  (self.stone_x, self.stone_y))
				self.new_stone()
				cleared_rows = 0
				while True:
					for i, row in enumerate(self.board[:-1]):
						if 0 not in row:
							self.board = remove_row(
							  self.board, i)
							cleared_rows += 1
							break
					else:
						break
				self.add_cl_lines(cleared_rows)
				return True
		return False
	
	def insta_drop(self):
		if not self.gameover and not self.paused:
			while(not self.drop(True)):
				pass
	
	def rotate_stone(self):
		if not self.gameover and not self.paused:
			new_stone = rotate_clockwise(self.stone)
			if not check_collision(self.board,
			                       new_stone,
			                       (self.stone_x, self.stone_y)):
				self.stone = new_stone
	
	def toggle_pause(self):
		self.paused = not self.paused
	
	def start_game(self):
		if self.gameover:
			if ip_addr == '':
				self.db.insert({'score' : self.score, 'level': self.level, 'time': time.time() - self.start_time})
			else:
				requests.post('http://' + ip_addr + ':5000/scores', data={'score' : self.score, 'level': self.level, 'time': time.time() - self.start_time, 'name': self.my_name})
			self.init_game()
			self.gameover = False 
	
	def speed_up(self):
		self.speed_level += 1
		newdelay = 1000-50*(self.level+self.speed_level-1)
		newdelay = 100 if newdelay < 100 else newdelay
		pygame.time.set_timer(pygame.USEREVENT+1, newdelay)

	def hold_block(self):
		if self.restorable_block == None:
			self.restorable_block = self.stone[:]
			self.new_stone()
		else:
			if self.already_restored:
				return
			self.restorable_block, self.stone = self.stone[:], self.restorable_block[:]
			self.stone_x = int(cols / 2 - len(self.stone[0])/2)
			self.stone_y = 0
		self.already_restored = True
	
	def toggle_bg_music(self):
		if not self.is_music_loaded:
			return
		if self.is_music_playing:
			pygame.mixer.music.pause()
		else:
			pygame.mixer.music.unpause()
		self.is_music_playing = not self.is_music_playing

	def die(self):
		print('Commit suicide!')
		self.gameover = True

	def run(self):
		global ip_addr
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		lambda:self.drop(True),
			'UP':		self.rotate_stone,
			'p':		self.toggle_pause,
			'SPACE':	self.start_game,
			's': self.speed_up,
			'h': self.hold_block,
			'm': self.toggle_bg_music,
			'd': self.die,
			'RETURN':	self.insta_drop
		}
		
		self.gameover = False
		self.paused = False
		
		dont_burn_my_cpu = pygame.time.Clock()
		is_printed = False
		while 1:
			self.screen.fill((0,0,0))
			if self.gameover:
				if ip_addr == '':
					if not is_printed:
						text = ''
						i = 0
						for item in iter(self.db):
							i += 1
							text += str(i) + ' => 총 시간: ' + str(round(float(item['time']))) + ', 점수: ' + str(item['score']) + ', 레벨: ' + str(item['level']) + '\n'
						print(text)
						is_printed = True
					self.center_msg("""게임 오버!\n점수: %d\n총 플레이 횟수: %d\n계속하려면 스페이스 바를 누르세요""" % (self.score, len(self.db.all())))
				else:
					if not is_printed:
						text = ''
						i = 0
						data = requests.get('http://' + ip_addr + ':5000/scores').json()['data']
						for item in iter(data):
							i += 1
							text += item['name'] + ' => 총 시간: ' + str(round(float(item['time']))) + ', 점수: ' + str(item['score']) + ', 레벨: ' + str(item['level']) + '\n'
						print(text)
						is_printed = True
					self.center_msg("""게임 오버!\n점수: %d\n계속하려면 스페이스 바를 누르세요""" % (self.score))
				
			else:
				if self.paused:
					self.center_msg("일시 정지")
				else:
					pygame.draw.line(self.screen,
						(255,255,255),
						(self.rlim+1, 0),
						(self.rlim+1, self.height-1))
					self.disp_msg("다음 블럭:", (
						self.rlim+cell_size,
						2))
					if ip_addr == '':
						self.disp_msg("최고 점수: %s\n현재 점수: %d\n\n현재 레벨: %d\n줄: %d\n시간: %d" % (str(self.high_score), self.score, self.level, self.lines, time.time() - self.start_time),
						(self.rlim+cell_size, cell_size*5))
					else:
						self.disp_msg("최고 점수: %s\n현재 점수: %d\n\n현재 레벨: %d\n줄: %d\n시간: %d" % (self.high_scorer + '의 ' + str(self.high_score) + '점', self.score, self.level, self.lines, time.time() - self.start_time),
						(self.rlim+cell_size, cell_size*5))
					self.disp_msg('홀드한 블럭:', 
						(self.rlim + cell_size, cell_size * 10))
					self.draw_matrix(self.bground_grid, (0,0))
					self.draw_matrix(self.board, (0,0))
					self.draw_matrix(self.stone,
						(self.stone_x, self.stone_y))
					self.draw_matrix(self.next_stone,
						(cols+1,2))
					if self.restorable_block != None:
						self.draw_matrix(self.restorable_block, 
							(cols+1, 11))
					
					
			pygame.display.update()
			
			for event in pygame.event.get():
				if event.type == pygame.USEREVENT+1:
					self.drop(False)
				elif event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					for key in key_actions:
						if event.key == eval("pygame.K_"
						+key):
							key_actions[key]()
					
			dont_burn_my_cpu.tick(maxfps)

if __name__ == '__main__':
	if len(sys.argv) == 2:
		ip_addr = sys.argv[1]
		try:
			print('Connecting to server http://' + ip_addr + ':5000/ ...')
			text = requests.get('http://' + ip_addr + ':5000/handshake', timeout=5).text
			if text.split('%&%')[0] != 'Hello From Tetris Scoreboard server':
				raise Exception('Handshake text doesn\'t match')
			current_time = time.time()
			print('Their time:', text.split('%&%')[1])
			print('Our time:', current_time)
			if abs(float(text.split('%&%')[1]) - current_time) > 100000:
				raise Exception('Time doesn\'t match')
			print('Message from server:' + text.split('%&%')[2])
		except Exception as e:
			print('Connection failed! Switching to local mode')
			print('Caused by: ', e)
			ip_addr = ''
	App = TetrisApp()
	App.run()