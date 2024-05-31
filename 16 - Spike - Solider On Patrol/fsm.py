import pyglet
from vector2d import Vector2D
from point2d import Point2D
from graphics import COLOUR_NAMES, window, ArrowLine
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from path import Path
from agent import Agent
from projectile import Projectile

class FSM:
	
	def __init__(self, hunter):
		
		self.hunter = hunter
		
		self.mode = self.hunter.mode

		self.firstModeStates = ["seek", "arrive slowly", "arrive normally", "arrive fast"]
		self.secondModeStates = ["shoot normally"]
  
		self.secondModeStates = self.secondModeStates[::-1]
		
		self.stateIndex = 0
		
	def currentState(self):
	 
		self.mode = self.hunter.mode
	
		if self.mode == "patrol":
			self.stateIndex = (int)(self.hunter.travelledDistance / 200) % 4
   
			return self.firstModeStates[self.stateIndex]
	
	def run(self, targetPos):

		self.mode = self.hunter.mode
	
		if self.mode == "patrol":
			self.stateIndex = (int)(self.hunter.travelledDistance / 200) % 4
			
			return self.hunter.followPath(self.firstModeStates[self.stateIndex])
		
		elif self.mode == "attack":
   
			projectileAcceleration = targetPos - self.hunter.pos
   
			if len(self.hunter.projectiles) < 1:
				if self.currentState() == "shoot normally":
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, projectileAcceleration.copy().normalise() * 1000.))
				else:
					self.hunter.projectiles.append(Projectile(self.hunter.world, self.hunter.color, self.hunter.pos.x, self.hunter.pos.y, projectileAcceleration.copy().normalise() * 1000.))
				