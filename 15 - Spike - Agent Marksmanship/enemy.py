from agent import Agent
import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from graphics import COLOUR_NAMES, window
from path import Path

class Enemy(Agent):
    
    def __init__(self, world=None, scale=10.0, mass=1.0, color='RED'):
        
        super().__init__(world, scale, mass, color)
        
        self.collisionRange = 15
        
        self.maxHealth = 100
        self.health = self.maxHealth
        self.alive = True

        self.health_bar = pyglet.shapes.Rectangle(0,0,0,0,color=COLOUR_NAMES['WHITE'],batch=window.get_batch("main"))
        self.health_current = pyglet.shapes.Rectangle(0,0,0,0,color=COLOUR_NAMES['RED'],batch=window.get_batch("main"))

        #Path
        self.path = Path()
        self.randomise_path()
        self.waypoint_threshold = 100.0

    
        
    def calculate(self, delta):      
        accel = self.follow_path()
        self.acceleration = accel    
        return accel
    

    def randomise_path(self):
        cx = self.world.cx # width
        cy = self.world.cy # height
        margin = min(cx, cy) * (1/6)
        self.path.create_random_path(10, margin, margin, cx-margin, cy-margin, looped = True)

    def follow_path(self):
        if self.path.is_finished():
            return self.arrive(self.path._pts[-1], 'normal')
        else:
            distance_to_way_point = self.pos.distance(self.path.current_pt())
            if distance_to_way_point <= self.waypoint_threshold:
                self.path.inc_current_pt()
            return self.seek(self.path.current_pt())

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