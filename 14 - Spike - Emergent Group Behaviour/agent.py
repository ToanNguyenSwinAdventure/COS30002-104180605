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
from graphics import COLOUR_NAMES, window, ArrowLine
from path import *
 
AGENT_MODES = {
    pyglet.window.key._1: 'seek',
    pyglet.window.key._2: 'arrive_slow',
    pyglet.window.key._3: 'separation',
    pyglet.window.key._4: 'combine',
    pyglet.window.key._5: 'flee',
    pyglet.window.key._6: 'pursuit',
    pyglet.window.key._7: 'follow_path',
    pyglet.window.key._8: 'wander',
    pyglet.window.key._9: 'alignment',
    pyglet.window.key._0: 'cohesion',
}

class Agent(object):

    # NOTE: Class Object (not *instance*) variables!
    DECELERATION_SPEEDS = {
        'slow': 0.1,
        'normal': 1.0,
        'fast': 2.0,
        ### ADD 'normal' and 'fast' speeds here
    }

    def __init__(self, world=None, scale=30.0, mass=1.0, mode='seek', hunter = None):
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
        self.anyHunter = self.world.hunter
        self.hunter_pos = None
        if self.anyHunter is not None:
            print("Hunter Available")
            self.hunter_pos = Vector2D(self.world.hunter.pos)

        self.isHunter = False
        if hunter == "hunter":
            print("HUNTER")
            self.max_speed = 2000.0
            self.isHunter = True
            self.color = "RED"
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
            batch=window.get_batch(("main"))
        )
        # self.wander info
        self.wander_circle = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['WHITE'], batch=window.get_batch("info"))
        self.info_wander_tgt = pyglet.shapes.Circle(0, 0, 0, color=COLOUR_NAMES['GREEN'], batch=window.get_batch("info"))
        self.wander_target = Vector2D(1, 0)
        self.wander_dist = 3.0 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 10.0 * scale
        self.bRadius = scale
        
        # limits?
        self.max_speed = 20.0 * scale
        self.max_force = 500.0

        self.cohesion_weight = 400.0
        self.separation_weight = 100.0
        self.alignment_weight = 200.0
        self.wander_weight = 100

        self.cohesion_radius = 100
        self.separation_radius = 50
        self.alignment_radius = 100
        
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

    def calculate(self,delta, close_neighbors = None, chased = False):
        # reset the steering force
        # print("CLOSE", close_neighbors)
        mode = self.mode
        target_pos = Vector2D(self.world.target.x, self.world.target.y)
        combined_force = Vector2D(0)
        accel = Vector2D(0)
        if self.isHunter:
            accel = self.pursuit(self.world.hunter)
        else:
            if chased:
                accel = self.flee(self.world.hunter.pos)
            elif mode == 'seek':
                accel = self.seek(target_pos)
            elif mode == "separation":
                combined_force = self.separation(close_neighbors) #* self.separation_weight
            elif mode == "combine":
                wander_accel = self.wander(delta)
                # wander_accel = Vector2D(0)
                cohesion_accel = self.cohesion(close_neighbors)
                alignment_accel = self.alignment(close_neighbors)
                print("CO AND AL", cohesion_accel, alignment_accel)

                combined_force = (wander_accel * self.wander_weight +
                                cohesion_accel * self.cohesion_weight +
                                alignment_accel * self.alignment_weight)
            elif mode == 'arrive_slow':
                accel = self.arrive(target_pos, 'slow')
            elif mode == 'flee':
                accel = self.flee(target_pos)
            elif mode == 'pursuit':
                accel = self.pursuit(self.world.hunter)
            elif mode == 'follow_path':
                accel = self.follow_path()
            elif mode == 'wander':
                accel = self.wander(delta)
            elif mode == 'alignment':
                accel = self.alignment(close_neighbors)
            elif mode == 'cohesion':
                accel = self.cohesion(close_neighbors)
            else:
                accel = Vector2D()
        # self.acceleration = accel
        # self.force = self.mass*accel
        # print("FORCE",self.force.length())
        combined_force = combined_force + accel
        return combined_force
    
    def hunter_in_distance(self):
        #Check if the hunter is in panic distances
        if isinstance(self.world.hunter, Agent):
            panic_distance = 150
            if (self.world.hunter.pos.distance(self.pos)) < panic_distance:
                self.flee(self.world.hunter.pos)
                return True
        else:
            return False

    def update(self, delta):
        ''' update vehicle position and orientation '''
        close_neighbors = self.get_neighbors(self.wander_radius)
        # acceleration = self.calculate(delta, close_neighbors=close_neighbors)
        self.force = self.calculate(delta, close_neighbors=close_neighbors)

        if isinstance(self.world.hunter, Agent):
            if self.hunter_in_distance():
                self.force = self.calculate(delta, close_neighbors=close_neighbors, chased = True)
        self.force.truncate(self.max_force) # <-- new force limiting code

        #new acceleration
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
        self.vehicle.x = self.pos.x+self.vehicle_shape[0].x
        self.vehicle.y = self.pos.y+self.vehicle_shape[0].y
        self.vehicle.rotation = -self.heading.angle_degrees()
        
        if self.anyHunter is not None:
            self.hunter_pos = Vector2D(self.world.hunter.pos)

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
        
        
                
    def get_neighbors(self, radius):
        #Return neighbors' agents
        radius = radius * 10
        neighbors = []
        for agent in self.world.agents:
            if agent != self:
                distance = (agent.pos - self.pos).length()
                if distance <= radius:
                    neighbors.append(agent)
        return neighbors 

    def closest(self, neighbors):
        #Find the closest agent neighbor
        min_distance = float('inf')
        closest_agent = None

        for agent in neighbors:
            # distance = (agent.pos - self.pos).length()
            distance = self.pos.distance(agent.pos)
            if distance < min_distance:
                min_distance = distance
                closest_agent = agent
        print("Closest", closest_agent)
        return closest_agent           

    def speed(self):
        return self.vel.length()
    
    def render(self):

        if self.mode == 'wander':
            wnd_pos = Vector2D(self.wander_dist, 0 )
            wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)
            self.wander_circle.position = (wld_pos.x, wld_pos.y)  
            self.wander_circle.radius = self.wander_radius
            # wnd_circle = pyglet.shapes.Circle(wld_pos.x,wld_pos.y, self.wander_radius,color = COLOUR_NAMES['GREEN'],batch=window.get_batch("info"))
            # wnd_circle.color(COLOUR_NAMES['GREEN'])

            # draw the wander target (little circle on the big circle)
            
            wnd_pos = (self.wander_target + Vector2D(self.wander_dist, 0))
            wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)
            self.info_wander_tgt.position = (wld_pos.x, wld_pos.y)  

            # wnd_circle = pyglet.shapes.Circle(wld_pos.x,wld_pos.y, 3, color = COLOUR_NAMES['RED'],batch=window.get_batch("info"))
            # wnd_circle.color(COLOUR_NAMES['RED'])

    #--------------------------------------------------------------------------
    def separation(self, close_neighbors):
        if not close_neighbors:
            return Vector2D()
        closest_agent = self.closest(close_neighbors)
        closest_agent_pos = closest_agent.pos
        target = ( self.pos - closest_agent_pos).normalise()
        to_target = target - self.pos.normalise()

        return to_target
    
    def cohesion(self, close_neighbors):
        center_of_mass = Vector2D()
        count = 0
        # if close_neighbors is not None:
        if len(close_neighbors) > 0:
            for agent in close_neighbors:
                center_of_mass += agent.pos
                count += 1
            if count > 0:
                center_of_mass /= count
                return center_of_mass
        
        return Vector2D()
        
    def alignment(self, close_neighbors):
        average_heading = Vector2D()
        count = 0
        
        if len(close_neighbors) >0:
        # if close_neighbors is not None:
            for agent in close_neighbors:
                average_heading += agent.heading
                count += 1

        if count > 0:
            average_heading /= len(close_neighbors)
            average_heading -= self.heading
            return average_heading
        else:
            return Vector2D()

    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)

    def flee(self, hunter_pos):
        ''' move away from hunter position '''
        # ## add panic distance (second)
        panic_distance = 150
        if (hunter_pos.distance(self.pos)) < panic_distance:
            desired_vel = (self.pos - hunter_pos).normalise() * self.max_speed
            return (desired_vel - self.vel)
        else:
            target_pos = Vector2D(self.world.target.x, self.world.target.y)
            return self.seek(target_pos)
        

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

        if self.isHunter:
            vision = 200
            for prey in self.world.agents:
                if self.pos.distance(prey.pos)< vision:
                    return self.seek(prey.pos)
                else:
                    return Vector2D()
        else:
            target_pos = Vector2D(self.world.target.x, self.world.target.y)
            self.seek(target_pos)
        return Vector2D()

    def randomise_path(self):
        cx = self.world.cx # width
        cy = self.world.cy # height
        margin = min(cx, cy) * (1/6)
        self.path.create_random_path(10, margin, margin, cx-margin, cy-margin)

    def follow_path(self):
        if self.path.is_finished():
            return self.arrive(self.path._pts[-1], 'slower')
        else:
            distance_to_way_point = self.pos.distance(self.path.current_pt())
            if distance_to_way_point <= self.waypoint_threshold:
                self.path.inc_current_pt()
            # return self.seek(self.path.current_waypoint(), 'fast')
            return self.seek(self.path.current_pt())
        
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
        print (wld_target.distance(self.pos))
        return self.seek(wld_target)
