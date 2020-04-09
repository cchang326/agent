# Simple pygame program

# Import and initialize the pygame library
import random
import math
import numpy as np
from numpy import linalg as la
import pygame
import utils

class Agent:
    def __init__(self, rect, id):
        self.loc = np.array(
            [random.uniform(rect[0] + rect[2] / 2, rect[0] + rect[2] - 1),
            random.uniform(rect[1] + rect[3] / 2, rect[1] + rect[3] - 1)])
        self.speed = 3 / 30
        self.max_speed = 2 * self.speed
        self.angular_speed = math.pi / 2
        self.angle = random.uniform(-math.pi / 4, 0)
        self.velocity = self.speed * np.array([math.cos(self.angle), math.sin(self.angle)])
        self.bound_ul = np.array([rect[0], rect[1]])
        self.bound_lr = np.array([rect[0] + rect[2], rect[1] + rect[3]])
        self.wall_buffer = 2
        self.last_direction_change = 0
        self.direction_change_period = random.uniform(100, 500)
        self.time = 0
        self.group_center = np.zeros(2)
        self.separation = np.zeros(2)
        self.group_velocity = np.zeros(2)
        self.id = id

    def update_randomwalk(self, timepassed):
        time = self.time + timepassed
        total_force = np.zeros(2)

        # random perturbation to direction
        if time - self.last_direction_change > self.direction_change_period:
            self.velocity += utils.rotate(self.velocity, random.uniform(-self.angular_speed, self.angular_speed))
            self.last_direction_change = time
        
        # avoid borders
        wall_force = np.zeros(2)
        for i in range(2):
            to_lower = self.loc[i] - self.bound_ul[i]
            to_upper = self.bound_lr[i] - self.loc[i]

            # Bounce
            if to_lower < 0:
                self.velocity[i] = abs(self.velocity[i])
                self.loc[i] = self.bound_ul[i]
            if to_upper < 0:
                self.velocity[i] = -abs(self.velocity[i])
                self.loc[i] = self.bound_lr[i]

            # Repelling force
            wall_force[i] += max((-1 / self.wall_buffer + 1 / to_lower), 0)
            wall_force[i] -= max((-1 / self.wall_buffer + 1 / to_upper), 0)
        total_force += wall_force

        # apply force
        self.velocity += total_force * timepassed
        speed = la.norm(self.velocity)
        if speed > self.max_speed:
            self.velocity *= self.max_speed / speed

        self.loc += self.velocity * timepassed
        self.time = time

    def wrap_around(self, location):
        loc = location
        if loc[0] < self.bound_ul[0]:
            loc[0] = self.bound_lr[0] - 1
        if loc[0] > self.bound_lr[0] - 1:
            loc[0] = self.bound_ul[0]
        if loc[1] < self.bound_ul[1]:
            loc[1] = self.bound_lr[1] - 1
        if loc[1] > self.bound_lr[1] - 1:
            loc[1] = self.bound_ul[1]
        return loc

    def cap_speed(self, velocity):
        speed = la.norm(velocity)
        if speed > self.max_speed:
            return velocity * (self.max_speed / speed)
        return velocity

    def update_boid(self, timepassed):
        self.velocity += 0.005 * (self.group_center - self.loc) / 30 # cohesion
        self.velocity += 0.02 * self.separation / 30 # separation
        self.velocity += 1 * self.group_velocity / 30
        self.velocity = self.cap_speed(self.velocity)

        # update location and wrap around
        self.loc += self.velocity * timepassed
        self.wrap_around(self.loc)
        self.time += timepassed

    def set_group_center(self, center, group_size):
        # group center excluding one self
        self.group_center = (center * group_size - self.loc) / (group_size - 1)

    def set_separation(self, separation):
        self.separation = separation

    def set_group_velocity(self, velocity, group_size):
        # group velocity excluding one self
        self.group_velocity = (velocity * group_size - self.velocity) / (group_size - 1)

class AgentsManager:
    def __init__(self, num, rect):
        self.agents = [Agent(rect, i) for i in range(num)]
        self.num_agents = num

    def update_randomwalk(self, timepassed):
        for agent in self.agents:
             agent.update_randomwalk(timepassed)

    def update_boid(self, timepassed):
        # calculate group center
        center = np.zeros(2)
        velocity = np.zeros(2)
        for agent in self.agents:
            center += agent.loc
            velocity += agent.velocity
        center /= self.num_agents
        velocity /= self.num_agents

        distances = [0 for i in range(self.num_agents)]
        for a in self.agents:
            a.set_group_center(center, self.num_agents)
            a.set_group_velocity(velocity, self.num_agents)
            
            # calculate separation force
            for b in [self.agents[i] for i in range(a.id + 1, self.num_agents)]:
                d = b.loc - a.loc
                if la.norm(d) < 30:
                    distances[a.id] += -d
                    distances[b.id] += d

        for a in self.agents:
            a.set_separation(distances[a.id])

        for a in self.agents:
            a.update_boid(timepassed)


class AgentVisualizer:
    def __init__(self):
        pygame.init()
        random.seed()

        self.WORLD_WIDTH = 500
        self.WORLD_HEIGHT = 500
        self.WORLD_RECT = pygame.Rect(0, 0, self.WORLD_WIDTH, self.WORLD_HEIGHT) # left, top, width, height
        self.screen = pygame.display.set_mode([self.WORLD_WIDTH, self.WORLD_HEIGHT])
        self.agentsManager = AgentsManager(50, self.WORLD_RECT)
        self.clock = pygame.time.Clock()
        self.clock.tick()

    def __del__(self):
        pygame.quit()

    def update(self):
        timepassed = self.clock.tick(30)
        self.screen.fill((255, 255, 255))
        self.agentsManager.update_boid(timepassed)
        for agent in self.agentsManager.agents:
            pygame.draw.circle(self.screen, (0, 0, 0), [int(loc) for loc in agent.loc], 3)

        # Flip the display
        pygame.display.flip()


if __name__ == '__main__':
    vis = AgentVisualizer()
    # Run until the user asks to quit
    running = True
    while running:

        # Did the user click the window close button?
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        vis.update()
