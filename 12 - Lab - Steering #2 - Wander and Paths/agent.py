'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for COS30002 AI for Games, by 
    Clinton Woodward <cwoodward@swin.edu.au>
    James Bonner <jbonner@swin.edu.au>
For class use only. Do not publically share or post this code without permission.

'''
import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from math import sin, cos, radians
from random import random, randrange, uniform
from graphics import COLOUR_NAMES, ArrowLine, window
from path import *

AGENT_MODES = {
    pyglet.window.key._1: 'seek',
    pyglet.window.key._2: 'arrive_slow',
    pyglet.window.key._3: 'arrive_normal',
    pyglet.window.key._4: 'arrive_fast',
    pyglet.window.key._5: 'flee',
    pyglet.window.key._6: 'pursuit',
    pyglet.window.key._7: 'follow_path',
    pyglet.window.key._8: 'wander',
}

class Agent(object):

    # NOTE: Class Object (not *instance*) variables!
    DECELERATION_SPEEDS = {
        'slow': 0.1,
        'normal': 1.0,
        'fast': 2.0,
        ### ADD 'normal' and 'fast' speeds here
    }

    def __init__(self, world=None, scale=30.0, mass=1.0, mode='seek'):
        # keep a reference to the world object
        self.world = world
        self.mode = mode
        # where am i and where am i going? random
        dir = radians(random()*360)
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)  # easy scaling of agent size
        
        #Force variables
        self.acceleration = Vector2D()  # current steering force
        self.force = Vector2D
        self.mass = mass
        # limits?
        self.max_speed = 2500.0
        #Path
        self.path = Path()
        self.randomise_path()
        self.waypoint_threshold = 100.0
        # data for drawing this agent
        self.color = 'ORANGE'
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
        # self.wander info
        self.wander_circle = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['WHITE'], batch=window.get_batch("info"))
        self.info_wander_tgt = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['GREEN'], batch=window.get_batch("info"))
        self.wander_target = Vector2D(1, 0)
        self.wander_dist = 1.0 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 10.0 * scale
        self.bRadius = scale
        
        # limits?
        self.max_speed = 20.0 * scale
        self.max_force = 500.0
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

    def calculate(self,delta):
        # reset the steering force
        mode = self.mode
        target_pos = Vector2D(self.world.target.x, self.world.target.y)
        if mode == 'seek':
            accel = self.seek(target_pos)
        elif mode == 'arrive_slow':
            accel = self.arrive(target_pos, 'slow')
        elif mode == 'arrive_normal':
            accel = self.arrive(target_pos, 'normal')
        elif mode == 'arrive_fast':
            accel = self.arrive(target_pos, 'fast')
        elif mode == 'flee':
            accel = self.flee(target_pos)
        # elif mode == 'pursuit':
        #    force = self.pursuit(self.world.hunter)
        elif mode == 'follow_path':
            accel = self.follow_path()
        elif mode == 'wander':
            print("wandering")
            accel = self.wander(delta)
        else:
            accel = Vector2D()
        self.acceleration = accel
        self.force = self.mass*accel
        # print("FORCE",self.force.length())

        return accel

    def update(self, delta):
        ''' update vehicle position and orientation '''
        acceleration = self.calculate(delta)
        # new velocity
        self.vel += acceleration * delta
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
        self.vehicle.x = self.pos.x+self.vehicle_shape[0].x
        self.vehicle.y = self.pos.y+self.vehicle_shape[0].y
        self.vehicle.rotation = -self.heading.angle_degrees()

        force = self.calculate(delta)
        force.truncate(self.max_force) # <-- new force limiting code
        # print("FORCE",force.length())
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

        if self.mode == 'follow_path' and self.path.renderable:
            self.path.renderable.draw()
        if self.mode == 'wander':
            self.render()


    def speed(self):
        return self.vel.length()
    
    def render(self):

        if self.mode == 'wander':
            ''' Draws the wander circle and target '''
            wnd_pos = Vector2D(self.wander_dist, 0)
            wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)
            self.wander_circle.position = (wld_pos.x, wld_pos.y)  
            self.wander_circle.radius = self.wander_radius

            wnd_pos = (self.wander_target + Vector2D(self.wander_dist, 0))
            wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)
            self.info_wander_tgt.position = (wld_pos.x, wld_pos.y)  
            

    #--------------------------------------------------------------------------

    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)

    def flee(self, hunter_pos):
        ''' move away from hunter position '''
        # print(hunter_pos.distance(self.pos))
        # ## add panic distance (second)
        panic_distance = 60
        if (hunter_pos.distance(self.pos)) < panic_distance:
            desired_vel = (self.pos - hunter_pos).normalise() * self.max_speed
            return (desired_vel - self.vel)
        else:
            # return self.seek(hunter_pos)
            desired_vel = (hunter_pos + self.pos).normalise() * self.max_speed 
            return (desired_vel - self.vel)
# add flee calculations (first)
        return Vector2D()
        

    def arrive(self, target_pos, speed):
        ''' this behaviour is similar to seek() but it attempts to arrive at
            the target position with a zero velocity'''
        decel_rate = self.DECELERATION_SPEEDS[speed]
        to_target = target_pos - self.pos
        dist = to_target.length()
        # print(self.vel.length())
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

    def pursuit(self, evader):
        ''' this behaviour predicts where an agent will be in time T and seeks
            towards that point to intercept it. '''
## OPTIONAL EXTRA... pursuit (you'll need something to pursue!)
        return Vector2D()

    def randomise_path(self):
        cx = self.world.cx # width
        cy = self.world.cy # height
        margin = min(cx, cy) * (1/6)
        # self.path.create_random_path(10, margin, margin, cx-margin, cy-margin)
        self.path.create_random_path(10, margin, margin, cx - margin, cy - margin,looped = True)

    def follow_path(self):
        if self.path.is_finished():
            return self.arrive(self.path._pts[-1], 'slow')
        else:
            # distance_to_way_point = self.pos.distance(self.path.current_pt())
            distance_to_way_point = (self.path.current_pt() - self.pos).length()

            if distance_to_way_point < self.waypoint_threshold:
                self.path.inc_current_pt()
            # return self.seek(self.path.current_waypoint(), 'fast')
            return self.arrive(self.path.current_pt(), 'normal')
            # return self.seek(self.path.current_pt())
        
    def wander(self, delta):
        ''' random wandering using a projected jitter circle '''
        wt = self.wander_target
        # this behaviour is dependent on the update rate, so this line must
        # be included when using time independent framerate.
        jitter_tts = self.wander_jitter * delta # this time slice
        # first, add a small random vector to the target's position
        wt += Vector2D(uniform(-1,1) * jitter_tts, uniform(-1,1) * jitter_tts)
        # re-project this new vector back on to a unit circle
        wt.normalise()
        # increase the length of the vector to the same as the radius
        # of the wander circle
        wt *= self.wander_radius
        # move the target into a position WanderDist in front of the agent
        target = wt + Vector2D(self.wander_dist, 0)
        # project the target into world space
        wld_target = self.world.transform_point(target, self.pos, self.heading, self.side)
        # and steer towards it
        return self.seek(wld_target)

    # def wander(self, delta):
    #     ''' random wandering using a projected jitter circle '''
    #     wander_target = self.wander_target
    #     # this behaviour is dependent on the update rate, so this line must
    #     # be included when using time independent framerate.
    #     jitter = self.wander_jitter * delta # this time slice
    #     # first, add a small random vector to the target's position
    #     wander_target += Vector2D(uniform(-1,1) * jitter, uniform(-1,1) * jitter)
    #     # re-project this new vector back on to a unit circle
    #     wander_target.normalise()
    #     # increase the length of the vector to the same as the radius
    #     # of the wander circle
    #     wander_target *= self.wander_radius
    #     # move the target into a position wander_dist in front of the agent
    #     wander_dist_vector = Vector2D(self.wander_dist, 0) #also used for rendering
    #     target = wander_target + Vector2D(self.wander_dist, 0)
    #     # set the position of the Agent’s debug circle to match the vectors we’ve created
    #     circle_pos = self.world.transform_point(wander_dist_vector, self.pos, self.heading, self.side,)
    #     self.info_wander_circle.x = circle_pos.x
    #     self.info_wander_circle.y = circle_pos.y
    #     self.info_wander_circle.radius = self.wander_radius
    #     # project the target into world space
    #     world_target = self.world.transform_point(target, self.pos, self.heading, self.side)
    #     #set the target debug circle position
    #     self.info_wander_target.x = world_target.x
    #     self.info_wander_target.y = world_target.y
    #     # and steer towards it
    #     return self.seek(world_target)  

