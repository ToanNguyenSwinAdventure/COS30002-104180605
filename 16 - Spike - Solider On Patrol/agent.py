'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for COS30002 AI for Games by 
	Clinton Woodward <cwoodward@swin.edu.au>
	James Bonner <jbonner@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''
import pyglet
from vector2d import Vector2D
from point2d import Point2D
from graphics import COLOUR_NAMES, window, ArrowLine
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from path import Path
# from fsm import FSM
# from projectile import Projectile

AGENT_MODES = {
	pyglet.window.key._1: 'patrol',
	pyglet.window.key._2: 'attack',
}

class Agent(object):

	# NOTE: Class Object (not *instance*) variables!
	DECELERATION_SPEEDS = {
		'slow': 0.9,
		'normal': 0.8,
		'fast': 0.6,
	}

	def __init__(self, world=None, scale=20.0, mass=1.0, color="RED"):
		# keep a reference to the world object
		self.world = world
		
		dir = radians(random()*360)
  
		self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
		self.vel = Vector2D()
  
		self.heading = Vector2D(sin(dir), cos(dir))
		self.side = self.heading.perp()
		self.scale = Vector2D(scale, scale)  # easy scaling of agent size
		self.acceleration = Vector2D() # current acceleration due to force
		self.mass = mass

		# data for drawing this agent
		self.color = color
		self.vehicle_shape = [
            Point2D(-20,  15),
            Point2D( 20,  0),
            Point2D(-20, -11)
        ]
		
		self.vehicle = pyglet.shapes.Triangle(
			self.pos.x+self.vehicle_shape[1].x, self.pos.y+self.vehicle_shape[1].y,
			self.pos.x+self.vehicle_shape[0].x, self.pos.y+self.vehicle_shape[0].y,
			self.pos.x+self.vehicle_shape[2].x, self.pos.y+self.vehicle_shape[2].y,
			color= COLOUR_NAMES[self.color],
			batch=window.get_batch("main")
		)
  
		# Force and speed limiting code
		self.max_speed = 20.0 * scale

        #Force Vectors
		self.force_vector = ArrowLine(Vector2D(0,0), Vector2D(0,0), colour=COLOUR_NAMES['LIGHT_GREEN'], batch=window.get_batch("info"))
		self.vel_vector = ArrowLine(Vector2D(0,0), Vector2D(0,0), colour=COLOUR_NAMES['LIGHT_BLUE'], batch=window.get_batch("info"))
		self.net_vectors = [
			ArrowLine(
				Vector2D(0,0), 
				Vector2D(0,0), 
				colour=COLOUR_NAMES['GREY'], 
				batch=window.get_batch("info")
			),
			ArrowLine(
				Vector2D(0,0), 
				Vector2D(0,0), 
				colour=COLOUR_NAMES['GREY'], 
				batch=window.get_batch("info")
			),
		]		
	def calculate(self, delta):

		raise NotImplementedError("This method should be overridden.")

	def update(self, delta):
		self.force = self.calculate(delta)
		self.acceleration = self.force / self.mass
		
		# new velocity
		self.vel += self.acceleration * delta
		# check for limits of new velocity
		self.vel.truncate(self.max_speed)
		# update position
		self.pos += self.vel * delta
		# update heading is non-zero velocity (moving)
		if self.vel.lengthSq() > 0.00000001:
			self.heading = self.vel.get_normalised()
			self.side = self.heading.perp()
		# treat world as continuous space - wrap new position if needed
		self.world.wrap_around(self.pos)
		# update the vehicle render position
		self.vehicle.x = self.pos.x + (self.vel.copy().normalise().x * (sqrt(3) / 3) * 20)
		self.vehicle.y = self.pos.y + (self.vel.copy().normalise().y * (sqrt(3) / 3) * 20)
		self.vehicle.rotation = -self.heading.angle_degrees()

		scaling = 0.5 # <-- scaling factor
		self.force_vector.position = self.pos
		self.force_vector.end_pos = self.pos + self.force * scaling
		# velocity
		self.vel_vector.position = self.pos
		self.vel_vector.end_pos = self.pos + self.vel * scaling
		self.net_vectors[0].position = self.pos+self.vel * scaling
		self.net_vectors[0].end_pos = self.pos + (self.force+self.vel) * scaling
		self.net_vectors[1].position = self.pos
		self.net_vectors[1].end_pos = self.pos + (self.force+self.vel) * scaling
	
	def speed(self):
		return self.vel.length()

	#--------------------------------------------------------------------------

	def seek(self, target_pos):
		''' move towards target position '''
		desired_vel = (target_pos - self.pos).normalise() * self.max_speed
		return (desired_vel - self.vel)
