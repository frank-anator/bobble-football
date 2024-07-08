import math

import tools


class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vX = 0
        self.vY = 0

        self.invincible = False
        self.attachedPlayer = None
        self.active = False
        self.plan = [0, 0]

    def tick(self, dt, players):
        if self.attachedPlayer is None:
            self.x += self.vX * dt
            self.y += self.vY * dt
            dir = math.atan2(self.vY, self.vX)+math.pi
            dX = math.cos(dir)*30*dt
            if abs(dX) > abs(self.vX):
                dX = -self.vX

            dY = math.sin(dir)*30*dt
            if abs(dY) > abs(self.vY):
                dY = -self.vY

            self.vX += dX
            self.vY += dY
            if self.invincible > 0:
                self.invincible -= dt
            
            else:
                for player in players:
                    if tools.dist(player.x, player.y, self.x, self.y) <= 40:
                        self.attachedPlayer = player
                        break
                self.invincible = 0

        else:
            self.x = self.attachedPlayer.x
            self.y = self.attachedPlayer.y
            self.vX = self.vY = 0


    def drag(self, mousePos, mouseClicked, camera):
        if not self.active:
            if mouseClicked:
                screenX, screenY = (self.x-camera.x, self.y-camera.y)
                if tools.dist(screenX, screenY, *mousePos) <= 15:
                    self.active = True

        else:
            if mouseClicked:
                screenX, screenY = (self.x-camera.x, self.y-camera.y)
                strength = min(tools.dist(screenX, screenY, *mousePos), 540)
                angle = math.atan2(screenY-mousePos[1], screenX-mousePos[0])
                self.plan = [strength, angle]

            else:
                self.active = False