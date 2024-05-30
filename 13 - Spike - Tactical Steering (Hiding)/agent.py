'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for COS30002 AI for Games, by 
    Clinton Woodward <cwoodward@swin.edu.au>
    James Bonner <jbonner@swin.edu.au>
For class use only. Do not publically share or post this code without permission.

'''
import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from graphics import COLOUR_NAMES, window, ArrowLine
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
    pyglet.window.key._9: 'hunter',
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
            self.isHunter = True
            self.color = "RED"
            self.vehicle_shape = [
            Point2D(-20,  15),
            Point2D( 20,  0),
            Point2D(-20, -11)  
            ]
            self.hiding_objects_line = []
            for obj in self.world.hide_objects:
                through_obj_line = pyglet.shapes.Line(
                    self.pos.x, 
                    self.pos.y, 
                    obj.pos.x,
                    obj.pos.y,
                    color = COLOUR_NAMES['RED'], 
                    batch= window.get_batch("info"))
                dict_obj_line = {"hide_obj": obj, "obj_line": through_obj_line}
                self.hiding_objects_line.append(dict_obj_line)
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


    def calculate(self,delta, chased = False):
        # reset the steering force
        mode = self.mode
        target_pos = Vector2D(self.world.target.x, self.world.target.y)

        if self.isHunter:
            for agent in self.world.agents:
                if self.is_prey_hiding(agent):
                    accel = self.avoid_objects()
                
            else:
                accel = self.pursuit(self.world.hunter)
        else:
            if chased:
                furthest_hide_obj = self.find_furthest_hide_object_from_hunter(self.world.hunter)

                if furthest_hide_obj:
                    print ("Chosen Hide Object:",furthest_hide_obj.pos)
                    hiding_position, _ = self.get_hiding_position_and_distance(furthest_hide_obj, self.world.hunter.pos)
                    print("Hiding Position:",hiding_position)
                    print(hiding_position)
                else:
                    hiding_position = None

                if hiding_position and self.world.hunter:
                    accel = self.seek(hiding_position)
                else:
                    accel = Vector2D()
            elif mode == 'seek':
                accel = self.seek(target_pos)
            elif mode == 'arrive_slow':
                accel = self.arrive(target_pos, 'slow')
            elif mode == 'arrive_normal':
                accel = self.arrive(target_pos, 'normal')
            elif mode == 'arrive_fast':
                accel = self.arrive(target_pos, 'fast')
            elif mode == 'flee':
                accel = self.flee(target_pos)
            elif mode == 'pursuit':
                accel = self.pursuit(self.world.hunter)
            elif mode == 'follow_path':
                accel = self.follow_path()
            elif mode == 'wander':
                print("wandering")
                accel = self.wander(delta)
            elif mode == 'hunter':
                pass
            else:
                accel = Vector2D()
        self.acceleration = accel
        self.force = self.mass*accel
        return accel
    
    def hide_behind_object(self, hunter_pos):
        best_hiding_spot = None
        best_distance = float('-inf')  # changed from 'inf' to '-inf'

        for hide_object in self.world.hide_objects:
            hiding_spot, distance = self.get_hiding_position_and_distance(hide_object, hunter_pos)
            if distance > best_distance:  # changed from '<' to '>'
                best_hiding_spot = hiding_spot
                best_distance = distance

        if best_hiding_spot:
            return self.arrive(best_hiding_spot, 'fast')

        return Vector2D()
    

    def find_furthest_hide_object_from_hunter(self, agent):
        if not self.world.hide_objects:  # if there are no hide objects
            return None
        objects = []
        for obj in self.world.hide_objects:
            distances = (obj.pos - agent.pos).length()
            o = {"obj": obj, "distances": distances}
            objects.append(o)
        #return object that has higher distances 
        max_distance_object = max(objects, key=lambda x: x["distances"])
        # max_distance_object["obj"].color = "GREEN"
        for h in self.world.hide_objects:
            if h == max_distance_object["obj"]:
                h.color = "GREEN"
            else:
                h.color = "WHITE"

        return max_distance_object['obj']
    
    def get_hiding_position_and_distance(self, hide_object, hunter_pos):
        offset = hunter_pos - hide_object.pos  # Use hunter_pos instead of hardcoded position
        hiding_distance = hide_object.radius + self.bRadius
        hiding_position = hide_object.pos - offset.normalise() * hiding_distance
        # offset =  hide_object.pos*2 - hunter_pos   # Use hunter_pos instead of hardcoded position
        # hiding_distance = hide_object.radius + self.bRadius
        # hiding_position = hide_object.pos - offset.normalise() * hiding_distance


        distance = hiding_position.distance(self.pos)
        # return offset, distance
        return hiding_position, distance

    def hunter_in_distance(self):
        #Check if the hunter is in panic distances
        if isinstance(self.world.hunter, Agent):
            
            # panic_distance = 150
            panic_distance = 750
            if (self.world.hunter.pos.distance(self.pos)) < panic_distance:
                self.flee(self.world.hunter.pos)
                return True
        else:
            return False
        
    def is_prey_hiding(self, prey):
        for hide_object in self.world.hide_objects:
            hiding_position, _ = prey.get_hiding_position_and_distance(hide_object, self.pos)
            if (prey.pos - hiding_position).length() < self.bRadius+100:
                return True
        return False
        # for p in prey:
        #     for hide_object in self.world.hide_objects:
        #         hiding_position, _ = p.get_hiding_position_and_distance(hide_object, self.pos)
        #         if (p.pos - hiding_position).length() < self.bRadius:
        #             return True
        #     return False
    
    def get_hiding_position_and_distance(self, hide_object, hunter_pos):
        offset = hunter_pos - hide_object.pos  # Use hunter_pos instead of hardcoded position
        hiding_distance = hide_object.radius + self.bRadius
        hiding_position = hide_object.pos - offset.normalise() * hiding_distance

        distance = hiding_position.distance(self.pos)
        return hiding_position, distance
    
    def avoid_objects(self):
        avoid_force = Vector2D()
        for obj in self.world.hide_objects:
            # Calculate vector from agent to object
            to_object = self.pos - obj.pos
            # Check if object is near
            if to_object.length() < obj.radius + self.bRadius:
                # Calculate a force to push the agent away from the object
                avoid_force += to_object.normalise() / to_object.length()
        return avoid_force
    
    def update(self, delta):
        ''' update vehicle position and orientation '''
        acceleration = self.calculate(delta)
        if isinstance(self.world.hunter, Agent):
            if self.hunter_in_distance():
                print("HUNTER IN DISTANCE")
                acceleration = self.calculate(delta, chased = True)
                # force = self.calculate(delta, chased = True)
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

        # print(self.anyHunter)
        if self.isHunter:
            for obj in self.hiding_objects_line:
                obj['obj_line'].x = self.pos.x
                obj['obj_line'].y = self.pos.y
                
                hide_pos_x = obj['hide_obj'].pos.x*2 - self.pos.x 
                hide_pos_y = obj['hide_obj'].pos.y*2 - self.pos.y 

                obj['obj_line'].x2 = hide_pos_x
                obj['obj_line'].y2 = hide_pos_y



        
        if self.anyHunter is not None:
            self.hunter_pos = Vector2D(self.world.hunter.pos)
        if isinstance(self.world.hunter, Agent):
            if self.hunter_in_distance():
                print("HUNTER IN DISTANCE")
                acceleration = self.calculate(delta, chased = True)
                # force = self.calculate(delta, chased = True)
        if self.mode == 'follow_path' and self.path.renderable:
            self.path.renderable.draw()
        if self.mode == 'wander':
            self.render()

    def speed(self):
        return self.vel.length()
    
    def render(self):

        if self.mode == 'wander':
            wnd_pos = Vector2D(self.wander_dist, 0 )
            wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)
            self.wander_circle.position = (wld_pos.x, wld_pos.y)  
            self.wander_circle.radius = self.wander_radius

            # draw the wander target (little circle on the big circle)
            
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
        # ## add panic distance (second)
        panic_distance = 150
        if (hunter_pos.distance(self.pos)) < panic_distance:
            desired_vel = (self.pos - hunter_pos).normalise() * self.max_speed
            #write a foreach loop to choose which hide_objects is closer
            # print(min([(self.pos - h.pos).length() for h in self.world.hide_objects]))
            min_target = min([(self.pos - h.pos).length() for h in self.world.hide_objects])
            target_pos = Vector2D(min_target)
            return self.seek(target_pos)
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
        self.path.create_random_path(10, margin, margin, cx-margin, cy-margin, looped = True)

    def follow_path(self):
        if self.path.is_finished():
            return self.arrive(self.path._pts[-1], 'normal')
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
        return self.seek(wld_target)
