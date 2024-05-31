import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from graphics import COLOUR_NAMES, window
from agent import Agent 

class Projectile(Agent):
	
	def __init__(self, world=None, color='GREEN', x=0., y=0., accel=Vector2D()):
		
		super().__init__(world, 5., 1.0, color)
		
		self.pos = Vector2D(x=x, y=y)
		
		self.acceleration = accel
		
		self.vehicle = pyglet.shapes.Circle(
			x=self.pos.x, y=self.pos.y,
			radius=5.0,
			color=COLOUR_NAMES[self.color],
			batch=window.get_batch("main")
		)
  
	def calculate(self):
		
		raise ValueError("This should not be called.")
		
	def update(self, delta):
		
		# new velocity
		self.vel += self.acceleration * delta
		
		# update position
		self.pos += self.vel * delta
		# update heading is non-zero velocity (moving)
		if self.vel.lengthSq() > 0.00000001:
			self.heading = self.vel.get_normalised()
			self.side = self.heading.perp()	  

		self.vehicle.x = self.pos.x
		self.vehicle.y = self.pos.y