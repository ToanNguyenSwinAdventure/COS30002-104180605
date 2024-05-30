import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from graphics import COLOUR_NAMES, window
from projectile import Projectile
from agent import Agent

class Hunter(Agent):
    
    def __init__(self, world=None, mass=1.0, color='ORANGE'):
        
        super().__init__(world, 0, mass, color)
        
        self.mode = "Rifle"
        self.mode_list = ["Rifle", "Hand Gun", "Rocket", "Hand Grenade"]
        
        self.type = 0
        self.projectile = None
        
        self.pos = Vector2D(self.world.cx / 2, 100.)
        self.heading = Vector2D(0., 1.)
        
    def projectileSpeed(self):
        if self.mode == "Rifle" or self.mode == "Hand Gun":
            return 2.
        elif self.mode == "Rocket" or self.mode == "Hand Grenade":
            return 1
        
    def changeMode(self):
        self.type =  (self.type + 1)% len(self.mode_list)
        self.mode = self.mode_list[self.type]
        print(f"Weapon changed to: {self.mode}")

    def projectilePower(self):
        if self.mode == "Hand Gun":
            return 1.
        elif self.mode == "Rocket":
            return 5.
        elif self.mode == "Rifle":
            return 10.
        elif self.mode == "Hand Grenade":
            return 15.
        
    def inaccurateAngleRate(self):
        if self.mode == "Rifle" or self.mode == "Rocket":
            return 0.
        elif self.mode == "Hand Gun" or self.mode == "Hand Grenade":
            return 0.5
        
    def calculate(self, delta):
        
        accel = self.attack()
        
        self.acceleration = accel
        
        return accel
    
    def attack(self):
        for enemy in self.world.enemy:
            return self.shoot_predicted_position(enemy)
    
    def shoot_predicted_position(self, enemy):
        """ This function calculates the new position after an amount of time
            Base on the formula: S = So + v*t + 1/2(a*t^2) 
            Where S: new position; So: old position; v: velocity; a: acceleration; t = amount of time
        
            Apply on current enemy and projectile
            We have: 
                New position of enemy: new_enemy_pos = enemy_pos + enemy_vel * time + 1/2(enemy_accel * time^2)
                New position of projectile: new_proj_pos = proj_pos + proj_vel * time + 1/2(proj_accel * time^2)
                
                If we want the new_enemy_pos and new_proj_pos to collide
                => new_enemy_pos = new_proj_pos
                <=> enemy_pos + enemy_vel * time + 1/2(enemy_accel * time^2) = proj_pos + proj_vel + time + 1/2(proj_accel * time^2)
                <=> 2 * enemy_pos + 2 * enemy_vel * time + enemy_accel * time^2 = 2 * proj_pos + 2 * proj_vel * time + proj_accel * time^2

                Since we want to calculate the projectile acceleration vector
                => proj_accel = (2*(enemy_pos - proj_pos) + 2*time(enemy_vel - proj_vel) + enemy_accel * time^2)/time^2
        """ 
        time_to_hit = 1/self.projectileSpeed()
        return (2 * (enemy.pos - self.pos) + 2 * time_to_hit * (enemy.vel - self.vel) + enemy.acceleration * time_to_hit * time_to_hit) / (time_to_hit * time_to_hit)
       

    def shoot(self):    
        if not self.projectile:
            self.projectile = Projectile(self.world, self.color, self.inaccurateAngleRate(), self.pos.x, self.pos.y, self.attack())  
            
    def update(self, delta):
        if self.vel.lengthSq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()
        # treat world as continuous space - wrap new position if needed
        self.world.wrap_around(self.pos)
        # update the vehicle render position
        self.vehicle.x = self.pos.x + (self.vel.copy().normalise().x * (sqrt(3) / 3) * 20)
        self.vehicle.y = self.pos.y + (self.vel.copy().normalise().y * (sqrt(3) / 3) * 20)
        self.vehicle.rotation = -self.heading.angle_degrees()

        for enemy in self.world.enemy:
            if self.projectile:
                self.projectile.update(delta)
                
                distanceFromEnemyToProjectile = (enemy.pos - self.projectile.pos).length()
                if distanceFromEnemyToProjectile <= enemy.collisionRange:
                    enemy.health = max(0, enemy.health - self.projectilePower())
                    self.projectile = None
                elif self.projectile.pos.x > self.world.cx or self.projectile.pos.x < 0 or self.projectile.pos.y > self.world.cy or self.projectile.pos.y < 0:
                    self.projectile = None
