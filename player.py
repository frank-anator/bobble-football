import math

import tools


class Player:
    def __init__(self, x, y, team):
        self.x = x
        self.y = y
        self.vX = 0
        self.vY = 0
        self.team = team
        self.active = False
        self.plan = [0, 0]

    def tick(self, mousePos, mouseClicked, camera):
        if not self.active:
            if mouseClicked:
                screenX, screenY = (self.x-camera.x, self.y-camera.y)
                if tools.dist(screenX, screenY, *mousePos) <= 25:
                    self.active = True

        else:
            if mouseClicked:
                screenX, screenY = (self.x-camera.x, self.y-camera.y)
                strength = min(tools.dist(screenX, screenY, *mousePos), 540)
                angle = math.atan2(screenY-mousePos[1], screenX-mousePos[0])
                self.plan = [strength, angle]

            else:
                self.active = False

    def collide(self, oX, oY, ovX, ovY):
        phi = math.atan2(oY-self.y, oX-self.x)
        theta1 = math.atan2(self.vY, self.vX)
        theta2 = math.atan2(ovY, ovX)
        v1 = tools.dist(0, 0, self.vX, self.vY)
        v2 = tools.dist(0, 0, ovX, ovY)
        self.vX = v2*math.cos(theta2-phi)*math.cos(phi)+v1*math.sin((theta1-phi))*math.cos(phi+math.pi/2)
        self.vY = v2*math.cos(theta2-phi)*math.sin(phi)+v1*math.sin((theta1-phi))*math.sin((phi+math.pi/2))
