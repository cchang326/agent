# Simple pygame program

# Import and initialize the pygame library
import pygame
import random
import math
import numpy as np

class Agent:
    def __init__(self, rect):
        self.x = random.uniform(rect[0], rect[0] + rect[2] - 1)
        self.y = random.uniform(rect[1], rect[1] + rect[3] - 1)
        self.speed = 2
        self.angle = random.uniform(0, math.pi * 2)
        self.world_rect = [rect[0], rect[1], rect[0] + rect[2], rect[1] + rect[3]]
        self.lastDirectionChangeTime = 0
        self.directionChangeDuration = random.uniform(1000, 2000)
        self.currTime = 0

    def update(self, timepassed):
        self.currTime += timepassed
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        # bounce back if hit border
        if (self.x < self.world_rect[0] or self.x > self.world_rect[2] or
            self.y < self.world_rect[1] or self.y > self.world_rect[3]):
            self.angle += math.pi

        # random perturbation to direction
        if (self.currTime - self.lastDirectionChangeTime > self.directionChangeDuration):
            new_angle = random.uniform(0, math.pi / 2)
            self.angle = self.angle * 0.8 + new_angle * 0.2
            self.lastDirectionChangeTime = self.currTime


class AgentsManager:
    def __init__(self, numAgents, rect):
        self.agents = [Agent(rect) for i in range(numAgents)]

    def update(self, timepassed):
        for agent in self.agents:
            agent.update(timepassed)

class AgentVisualizer:
    def __init__(self):
        pygame.init()
        random.seed()

        self.WORLD_WIDTH = 500
        self.WORLD_HEIGHT = 500
        self.WORLD_RECT = pygame.Rect(0, 0, self.WORLD_WIDTH, self.WORLD_HEIGHT) # left, top, width, height
        self.screen = pygame.display.set_mode([self.WORLD_WIDTH, self.WORLD_HEIGHT])
        self.agentsManager = AgentsManager(100, self.WORLD_RECT)
        self.clock = pygame.time.Clock()
        self.clock.tick()

    def __del__(self):
        pygame.quit()

    def update(self):
        timepassed = self.clock.tick(30)
        self.screen.fill((255, 255, 255))
        self.agentsManager.update(timepassed)
        for agent in self.agentsManager.agents:
            pygame.draw.circle(self.screen, (0, 0, 0), (int(agent.x), int(agent.y)), 2)

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

