import pygame
import math
import serial
from queue import PriorityQueue

WIDTH = 600
LENGTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (75, 180, 59)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
TAN = (210, 180, 140)
GOLD = (255, 215, 25)

class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == TAN

	def is_open(self):
		return self.color == GOLD

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == RED

	def is_end(self):
		return self.color == GREEN

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = RED

	def make_closed(self):
		self.color = TAN

	def make_open(self):
		self.color = GOLD

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = GREEN

	def make_path(self):
		self.color = RED

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		#Find neighbor nodes given current position and orientation

		self.neighbors = []
		count = 0
		if self.orien == 1:
			if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # RIGHT
				self.neighbors.append(grid[self.row + 1][self.col])
				self.neighbors[count].orien = 1
				count += 1
				
			if self.col > 0 and self.row < self.total_rows - 1 and not grid[self.row + 1][self.col - 1].is_barrier(): # UP-RIGHT
				self.neighbors.append(grid[self.row + 1][self.col - 1])
				self.neighbors[count].orien = 0
				count += 1
			
			if self.row < self.total_rows - 1 and self.col < self.total_rows - 1 and not grid[self.row + 1][self.col + 1].is_barrier(): # DOWN-RIGHT
				self.neighbors.append(grid[self.row + 1][self.col + 1])
				self.neighbors[count].orien = 2
				count += 1
		
		elif self.orien == 0:
			if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # UP
				self.neighbors.append(grid[self.row][self.col - 1])
				self.neighbors[count].orien = 0
				count += 1
			
			if self.col > 0 and self.row < self.total_rows - 1 and not grid[self.row + 1][self.col - 1].is_barrier(): # UP-RIGHT
				self.neighbors.append(grid[self.row + 1][self.col - 1])
				self.neighbors[count].orien = 1
				count += 1
				
			if self.row > 0 and self.col > 0 and not grid[self.row - 1][self.col - 1].is_barrier(): # UP-LEFT
				self.neighbors.append(grid[self.row - 1][self.col - 1])
				self.neighbors[count].orien = 3
				count += 1
			
		elif self.orien == 2:
			if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # DOWN
				self.neighbors.append(grid[self.row][self.col + 1])
				self.neighbors[count].orien = 2
				count += 1

			if self.col < self.total_rows - 1 and self.row > 0 and not grid[self.row - 1][self.col + 1].is_barrier(): # DOWN-LEFT
				self.neighbors.append(grid[self.row - 1][self.col + 1])
				self.neighbors[count].orien = 3
				count += 1
			
			if self.row < self.total_rows - 1 and self.col < self.total_rows - 1 and not grid[self.row + 1][self.col + 1].is_barrier(): # DOWN-RIGHT
				self.neighbors.append(grid[self.row + 1][self.col + 1])
				self.neighbors[count].orien = 1
				count += 1
				
		elif self.orien == 3:
			if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # LEFT
				self.neighbors.append(grid[self.row - 1][self.col])
				self.neighbors[count].orien = 3
				count += 1

			if self.row > 0 and self.col > 0 and not grid[self.row - 1][self.col - 1].is_barrier(): # UP-LEFT
				self.neighbors.append(grid[self.row - 1][self.col - 1])
				self.neighbors[count].orien = 0
				count += 1
			
			if self.col < self.total_rows - 1 and self.row > 0 and not grid[self.row - 1][self.col + 1].is_barrier(): # DOWN-LEFT
				self.neighbors.append(grid[self.row - 1][self.col + 1])
				self.neighbors[count].orien = 2
				count += 1

	def __lt__(self, other):
		return False


def dis(p1, p2):
	#effective distance from node p1 to goal node p2
	x1, y1 = p1
	x2, y2 = p2
	
	dx = abs(x1 - x2)
	dy = abs(y1 - y2)
	
	dist = 0.414*min(dx, dy) + max(dx, dy)
	
	return dist


def reconstruct_path(came_from, current, draw):
	#Record shortest path using 'came_from' variable and translate it into commands in 'inst' variable to export

	path = []
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()
		print(current)

		path.append(current)

	inst = []
	orien = 1
	for i in range(len(path) - 1):
		if path[i].col == path[i + 1].col or path[i].row == path[i + 1].row: #moving straight
			inst.append(0)
			
		elif path[i].col < path[i + 1].col and path[i].row > path[i + 1].row: #moving up-right
			if orien == 0:
				inst.append(45)
				orien = 1
			elif orien == 1:
				inst.append(-45)
				orien = 0
				
		elif path[i].col < path[i+1].col or path[i].row < path[i + 1].row: #moving down-right
			if orien == 1:
				inst.append(45)
				orien = 2
			elif orien == 2:
				inst.append(-45)
				orien = 1

def algorithm(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = dis(start.get_pos(), end.get_pos())

	open_set_hash = {start}

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)

		if current == end:
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

		if current == start:
			current.orien = 1

		current.update_neighbors(grid)
		

		for neighbor in current.neighbors:
			if neighbor.row == current.row or neighbor.col == current.col:
				temp_g_score = g_score[current] + 1
			else:
				temp_g_score = g_score[current] + 1.414

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + dis(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()

		if current != start:
			current.make_closed()

	return False


def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)

	return grid


def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
	win.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()


def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col


def main(win, width):
	ROWS = 50
	grid = make_grid(ROWS, width)

	start = None
	end = None

	run = True
	while run:
		draw(win, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]: # LEFT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				if not start and spot != end:
					start = spot
					start.make_start()

				elif not end and spot != start:
					end = spot
					end.make_end()

				elif spot != end and spot != start:
					spot.make_barrier()

			elif pygame.mouse.get_pressed()[2]: # RIGHT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				spot.reset()
				if spot == start:
					start = None
				elif spot == end:
					end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end:
					algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

				if event.key == pygame.K_c:
					start = None
					end = None
					grid = make_grid(ROWS, width)

	pygame.quit()

main(WIN, WIDTH)