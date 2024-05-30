import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from graphics import COLOUR_NAMES, window, ArrowLine

class Agent(object):
    
    def __init__(self, world=None, scale=10.0, mass=1.0, color='ORANGE'):
        
        self.world = world
        
        dir = radians(random()*360)
        
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)  
        self.acceleration = Vector2D()  
        self.mass = mass
        
        self.max_speed = scale * 10
        
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

        ### wander details
        self.wander_target = Vector2D(1, 0)
        self.wander_dist = 1.0 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 10.0 * scale
        self.bRadius = scale
        # Force and speed limiting code
        self.max_speed = 20.0 * scale
        self.max_force = 500.0

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
        #self.vel.truncate(self.max_speed)
        # update position
        self.pos += self.vel * delta
        # update heading is non-zero velocity (moving)
        if self.vel.lengthSq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()
        # treat world as continuous space - wrap new position if needed
        self.world.wrap_around(self.pos)
        # update the vehicle render position
        self.vehicle.x = self.pos.x+self.vehicle_shape[0].x
        self.vehicle.y = self.pos.y+self.vehicle_shape[0].y
        # self.vehicle.x = self.pos.x + (self.vel.copy().normalise().x * (sqrt(3) / 3) * 20)
        # self.vehicle.y = self.pos.y + (self.vel.copy().normalise().y * (sqrt(3) / 3) * 20)
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
    
    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)
    
    def flee(self, other):
        from_target = self.pos - other.pos

        desiredVel = from_target.normalise() * self.max_speed
        return (desiredVel - self.vel) * 20
    
    def wander(self, delta):
        ''' random wandering using a projected jitter circle '''
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
        # and steer towards it

        return self.seek(world_target)
   
