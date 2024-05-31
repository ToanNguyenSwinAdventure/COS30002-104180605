import pyglet
from vector2d import Vector2D
from point2d import Point2D
from graphics import COLOUR_NAMES, window, ArrowLine
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from path import Path
from agent import Agent

class Enemy(Agent):
	
	def __init__(self, world=None, scale=1.0, mass=1.0):
		
		super().__init__(world, scale, mass)
  
		self.collisionRange = 15
		
		self.maxHealth = 100
		self.health = self.maxHealth
		self.alive = True
		
		self.health_bar = pyglet.shapes.Rectangle(0,0,0,0,color=COLOUR_NAMES['WHITE'],batch=window.get_batch("main"))
		self.health_current = pyglet.shapes.Rectangle(0,0,0,0,color=COLOUR_NAMES['RED'],batch=window.get_batch("main"))
  
		### wander details
		self.wander_target = Vector2D(1, 0)
		self.wander_dist = 1.0 * scale
		self.wander_radius = 1.0 * scale
		self.wander_jitter = 10.0 * scale
		self.bRadius = scale
  
	def calculate(self, delta):
	 
		accel = self.wander(delta)

		self.acceleration = accel
		
		return accel
  
	def update(self, delta):
		if self.isAlive() == True: 
			super().update(delta)
			self.render()

	def isAlive(self):
		if self.health > 0:
			self.alive = True
			return True
		elif self.health <= 0: 
			self.alive = False
			return False	
		

	def wander(self, delta):

		wander_target = self.wander_target
		# this behaviour is dependent on the update rate, so this line must
		# be included when using time independent framerate.
		jitter = self.wander_jitter * delta # this time slice
		# first, add a small random vector to the target's position
		wander_target += Vector2D(uniform(-1,1) * jitter, uniform(-1,1) * jitter)
		# re-project this new vector back on to a unit circle
		wander_target.normalise()
		# increase the length of the vector to the same as the radius
		# of the wander circle
		wander_target *= self.wander_radius
		# move the target into a position wander_dist in front of the agent
		wander_dist_vector = Vector2D(self.wander_dist, 0) #also used for rendering
		target = wander_target + Vector2D(self.wander_dist, 0)

		# project the target into world space
		world_target = self.world.transform_point(target, self.pos, self.heading, self.side)

		return self.seek(world_target)
	
	def render(self):
		health_ratio = self.health / self.maxHealth
		bar_width = 100
		bar_height = 5

		#White
		self.health_bar.x =  self.pos.x - bar_width / 2
		self.health_bar.y =  self.pos.y  + 50
		self.health_bar.width =   bar_width 
		self.health_bar.height =   5 + bar_height
		#RED
		self.health_current.x =  self.pos.x - bar_width / 2
		self.health_current.y =  self.pos.y  + 50
		self.health_current.width =   bar_width * health_ratio
		self.health_current.height =   5 + bar_height