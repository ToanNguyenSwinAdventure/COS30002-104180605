'''A 2d world that supports agents with steering behaviour

Created for COS30002 AI for Games, by Clinton Woodward <cwoodward@swin.edu.au>
For class use only. Do not publically share or post this code without permission.

'''

from random import random, randrange, uniform
from vector2d import Vector2D
from matrix33 import Matrix33
import pyglet
from graphics import COLOUR_NAMES, window
from agent import Agent, AGENT_MODES  # Agent with seek, arrive, flee and pursuit


class HideObject(object):
    def __init__(self, world=None, position=None, radius=5, color='WHITE'):
        self.world = world
        self.pos = position if position is not None else self.randomise_loc()
        self.radius = randrange(50, 70)
        self.color = color
        self.agents = []
        self.hide_circle = pyglet.shapes.Circle(
            self.pos.x, self.pos.y, self.radius, color=COLOUR_NAMES[self.color], batch=window.get_batch("main")
        )

    def randomise_loc(self):
        ''' Randomise the location within the world's boundaries '''
        return Vector2D(randrange(self.world.cx), randrange(self.world.cy))

    def update(self,delta = None):
        self.agents.clear()
        self.render()
        # for prey in self.world.get_preys():
        #     if self.is_inside(prey):
        #         self.agents.append(prey)

			

    def is_inside(self, agent):
        ''' Check if the agent is inside the hide object's radius '''
        return self.pos.distance(agent.pos) < self.radius

    def render(self):
        # Update the position of the circle
        self.hide_circle.x = self.pos.x
        self.hide_circle.y = self.pos.y
        self.hide_circle.radius = self.radius
        
        # If there are agents inside this HideObject, then change the color to red
        if len(self.agents) > 0:
            self.color = 'RED'
        else:
            self.color = 'WHITE'
        
        # Update the color of the circle
        self.hide_circle.color = COLOUR_NAMES[self.color]

	

class World(object):
	def __init__(self, cx, cy):
		self.cx = cx
		self.cy = cy
		self.hunter = None
		self.agents = []
		self.paused = True
		self.showinfo = True
		self.target = pyglet.shapes.Star(
			cx / 2, cy / 2, 
			30, 1, 4, 
			color=COLOUR_NAMES['RED'], 
			batch=window.get_batch("main")
		)
		self.hide_objects = [HideObject(self, Vector2D(200, 200), 50),
						HideObject(self, Vector2D(600, 400), 50)
						]

	def update(self, delta):
		if not self.paused:
			for agent in self.agents:
				agent.update(delta)
			if self.hunter is not None:
				self.hunter.update(delta)
			for hide_obj in self.hide_objects:
				hide_obj.update(delta = delta)

	def wrap_around(self, pos):
		''' Treat world as a toroidal space. Updates parameter object pos '''
		max_x, max_y = self.cx, self.cy
		if pos.x > max_x:
			pos.x = pos.x - max_x
		elif pos.x < 0:
			pos.x = max_x - pos.x
		if pos.y > max_y:
			pos.y = pos.y - max_y
		elif pos.y < 0:
			pos.y = max_y - pos.y

	def transform_points(self, points, pos, forward, side, scale):
		''' Transform the given list of points, using the provided position,
			direction and scale, to object world space. '''
		# make a copy of original points (so we don't trash them)
		wld_pts = [pt.copy() for pt in points]
		# create a transformation matrix to perform the operations
		mat = Matrix33()
		# scale,
		mat.scale_update(scale.x, scale.y)
		# rotate
		mat.rotate_by_vectors_update(forward, side)
		# and translate
		mat.translate_update(pos.x, pos.y)
		# now transform all the points (vertices)
		mat.transform_vector2d_list(wld_pts)
		# done
		return wld_pts
	
	def input_mouse(self, x, y, button, modifiers):
		if button == 1:  # left
			self.target.x = x
			self.target.y = y
	
	def input_keyboard(self, symbol, modifiers):
		if symbol == pyglet.window.key.P:
			self.paused = not self.paused
		elif symbol == pyglet.window.key.H:
			# self.hunter = not self.hunter
			self.hunter = Agent(self,hunter = "hunter")
			
		elif  symbol == pyglet.window.key.K:
			self.hunter = None	
		elif  symbol == pyglet.window.key.A:
			self.agents.append(Agent(self))
		elif  symbol == pyglet.window.key.D:
			self.agents.pop()	
		elif  symbol == pyglet.window.key.R:
			for agent in self.agents:
				agent.randomise_path()

			# self.agents.append(Agent(self, type ="hunter"))
		elif symbol in AGENT_MODES:
			for agent in self.agents:
				agent.mode = AGENT_MODES[symbol]

	def transform_point(self, point, pos, forward, side):
		''' Transform the given single point, using the provided position,
        and direction (forward and side unit vectors), to object world space. '''
		# make a copy of the original point (so we don't trash it)
		wld_pt = point.copy()
		# create a transformation matrix to perform the operations
		mat = Matrix33()
		# rotate
		mat.rotate_by_vectors_update(forward, side)
        # rotate
		mat.rotate_by_vectors_update(forward, side)
        # and translate
		mat.translate_update(pos.x, pos.y)
        # now transform the point (in place)
		mat.transform_vector2d(wld_pt)
        # done
		return wld_pt

