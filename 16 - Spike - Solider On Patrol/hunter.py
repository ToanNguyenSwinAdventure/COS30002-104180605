import pyglet
from vector2d import Vector2D
from point2d import Point2D
from graphics import COLOUR_NAMES, window, ArrowLine
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from path import Path
from agent import Agent
from fsm import FSM
from projectile import Projectile

class Hunter(Agent):
	
	def __init__(self, world=None, scale=20.0, mass=1.0, color='ORANGE', mode='patrol'):
		
		super().__init__(world, scale, mass, color=color)
		
		self.weapon_mode = "Rifle"
		self.mode_list = ["Rifle", "Hand Gun", "Rocket", "Hand Grenade"]

		self.type = 0
		self.projectile = None

		self.vehicle_shape = [
            Point2D(-10,  6),
            Point2D( 10,  0),
            Point2D(-10, -6)
        ]
		
		self.vehicle = pyglet.shapes.Triangle(
			self.pos.x+self.vehicle_shape[1].x, self.pos.y+self.vehicle_shape[1].y,
			self.pos.x+self.vehicle_shape[0].x, self.pos.y+self.vehicle_shape[0].y,
			self.pos.x+self.vehicle_shape[2].x, self.pos.y+self.vehicle_shape[2].y,
			color= COLOUR_NAMES[self.color],
			batch=window.get_batch("main")
		)

		self.mode = mode
		
		self.path = Path()
		self.randomise_path()
		self.waypoint_threshold = 2.0
  
		self.travelledDistance = 0.
  
		self.FSM = FSM(self)
  
		self.projectiles = []

	def projectileSpeed(self):
		if self.weapon_mode == "Rifle" or self.weapon_mode == "Hand Gun":
			return 2.
		elif self.weapon_mode == "Rocket" or self.weapon_mode == "Hand Grenade":
			return 1
        
	def changeMode(self):
		self.type =  (self.type + 1)% len(self.mode_list)
		self.weapon_mode = self.mode_list[self.type]
		print(f"Weapon changed to: {self.weapon_mode}")

	def projectilePower(self):
		if self.weapon_mode == "Hand Gun":
			return 1.
		elif self.weapon_mode == "Rocket":
			return 5.
		elif self.weapon_mode == "Rifle":
			return 10.
		elif self.weapon_mode == "Hand Grenade":
			return 15.
        
	def inaccurateAngleRate(self):
		if self.weapon_mode == "Rifle" or self.weapon_mode == "Rocket":
			return 0.
		elif self.weapon_mode == "Hand Gun" or self.weapon_mode == "Hand Grenade":
			return 0.5
        
	def attack(self):
		for enemy in self.world.enemies:
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
              

	def calculate(self, delta):
	 
		targetPos = Vector2D(self.world.target.x, self.world.target.y)
		
		accel = Vector2D()
		if self.mode == "patrol":
			accel = self.FSM.run(targetPos)
		elif self.mode == "attack":
			accel = self.attack()
			self.vel = Vector2D()

			self.FSM.run(targetPos)
		
		self.acceleration = accel
		
		return accel

	def update(self, delta):
		self.force = self.calculate(delta)
		print(self.force)
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
  
		self.travelledDistance += (self.vel * delta).copy().length()

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


		# Update the deletability of projectiles
		i = 0
		while i < len(self.projectiles):
			# Find the nearest enemy
			nearestEnemy = None
			distanceToNearestEnemy = float('inf')
			for enemy in self.world.enemies:
				distanceToEnemy = (self.projectiles[i].pos - enemy.pos).length()
				if distanceToEnemy < distanceToNearestEnemy:
					nearestEnemy = enemy
					distanceToNearestEnemy = distanceToEnemy

			# Collide with the enemy
			if distanceToNearestEnemy < nearestEnemy.collisionRange:
				nearestEnemy.health = max(0., nearestEnemy.health - 10)
				del self.projectiles[i]
			# Out of the map
			elif self.projectiles[i].pos.x > self.world.cx or self.projectiles[i].pos.x < 0 or self.projectiles[i].pos.y > self.world.cy or self.projectiles[i].pos.y < 0:
				del self.projectiles[i]
			else:
				i += 1
  
		self.path.renderable.draw()
  
	def randomise_path(self):
		cx = 640  # width
		cy = 360  # height
		
		min_dist = 15  # the minimum distance between the waypoints
		
		minx = cx * 0.75
		miny = cy * 0.75
		
		maxx = cx * 1
		maxy = cy * 1
		
		self.path.create_random_path(min_dist, minx, miny, maxx, maxy)
		
	def followPath(self, decelerationType="arrive slowly"):
		# If heading to final point (is_finished?), return a slow down force vector (Arrive)
		if self.path.is_finished():
			return self.arrive_slow(self.path._pts[-1])
		else:
			distance_to_way_point = self.pos.distance(self.path.current_pt())
			# If within threshold distance of current way point, inc to next in path
			if distance_to_way_point <= self.waypoint_threshold:
				self.path.inc_current_pt()
	
			if decelerationType == "seek":
				return self.seek(self.path.current_pt())
			elif decelerationType == "arrive slowly":
				return self.arriveSlow(self.path.current_pt())
			elif decelerationType == "arrive normaly":
				return self.arriveNormal(self.path.current_pt())
			else:
				return self.arriveFast(self.path.current_pt())

	def arriveSlow(self, target_pos):

		decel_rate = self.DECELERATION_SPEEDS["slow"]
		to_target = target_pos - self.pos
		dist = to_target.length()
		if dist > 0:
			# calculate the speed required to reach the target given the
			# desired deceleration rate
			speed = dist / decel_rate
			# make sure the velocity does not exceed the max
			speed = min(speed, self.max_speed)
			# from here proceed just like Seek except we don't need to
			# normalize the to_target vector because we have already gone to the
			# trouble of calculating its length for dist.
			desired_vel = to_target * (speed / dist)
			return (desired_vel - self.vel)
		return Vector2D(0, 0)

	def arriveNormal(self, target_pos):

		decel_rate = self.DECELERATION_SPEEDS["normal"]
		to_target = target_pos - self.pos
		dist = to_target.length()
		if dist > 0:
			# calculate the speed required to reach the target given the
			# desired deceleration rate
			speed = dist / decel_rate
			# make sure the velocity does not exceed the max
			speed = min(speed, self.max_speed)
			# from here proceed just like Seek except we don't need to
			# normalize the to_target vector because we have already gone to the
			# trouble of calculating its length for dist.
			desired_vel = to_target * (speed / dist)
			return (desired_vel - self.vel)
		return Vector2D(0, 0)

	def arriveFast(self, target_pos):

		decel_rate = self.DECELERATION_SPEEDS["fast"]
		to_target = target_pos - self.pos
		dist = to_target.length()
		if dist > 0:
			# calculate the speed required to reach the target given the
			# desired deceleration rate
			speed = dist / decel_rate
			# make sure the velocity does not exceed the max
			speed = min(speed, self.max_speed)
			# from here proceed just like Seek except we don't need to
			# normalize the to_target vector because we have already gone to the
			# trouble of calculating its length for dist.
			desired_vel = to_target * (speed / dist)
			return (desired_vel - self.vel)
		return Vector2D(0, 0)