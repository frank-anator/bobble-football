import math
import random

import pygame.draw

import tools
from ball import Ball
from player import Player
from text import Text


class Field:
    TRANSITION = 0
    DEFENDERS = 1
    ATTACKERS = 2
    QUARTEREND = 3
    GAME = 4
    CUTSCENE = 5
    down_to_words = {
        0:"1st",
        1:"2nd",
        2:"3rd",
        3:"4th",
        4:"5th"
    }
    def __init__(self):
        self.players = []
        self.time = 0
        self.selected = 0
        self.prevMouseClicked = False
        self.attacking = 0
        self.leftteam = 0

        self.stage = Field.TRANSITION
        self.activeButton = False

        self.gameStartTime = 0
        self.released = False
        self.ball = Ball(180, 360)
        self.lineofscrimmage = 360
        self.firstdownline = 540
        self.make_players_default(center=self.lineofscrimmage, leftteam=self.leftteam, attackteam=self.attacking)
        self.message = ""
        self.messageColor = ""
        self.points = [0, 0]
        self.down = 0
        self.yards = 10
        self.cutsceneStart = 0
        self.evaluated = False
        self.instructionsButtonHover = False
        self.instructions = False

        self.quarter = 0
        self.gameTime = 0

    def make_players_default(self, center=900, leftteam=0, attackteam=0):
        self.players = []
        for i in range(110, 600, 75):
            self.players.append(Player(center-90, i, leftteam))
            self.players.append(Player(center+90, i, 1-leftteam))

        if leftteam == attackteam:
            self.players.append(Player(center-180, 300, leftteam))
            self.players.append(Player(center+360, 260, 1-leftteam))

        else:
            self.players.append(Player(center+180, 300, 1-leftteam))
            self.players.append(Player(center-360, 260, leftteam))

    def release(self):
        for player in self.players:
            player.vY = math.sin(player.plan[1])*player.plan[0]
            player.vX = math.cos(player.plan[1])*player.plan[0]
            player.plan = [0, 0]

        self.ball.vY = math.sin(self.ball.plan[1])*self.ball.plan[0]
        self.ball.vX = math.cos(self.ball.plan[1])*self.ball.plan[0]
        self.ball.plan = [0, 0]

    def tick(self, mousePos, mouseClicked, camera, dt):
        self.time += dt
        if self.stage == Field.TRANSITION:
            if 350 <= mousePos[0] <= 550 and 450 <= mousePos[1] <= 550:
                self.activeButton = True
                if mouseClicked and not self.prevMouseClicked:
                    if self.selected == self.attacking:
                        self.stage = Field.ATTACKERS

                    else:
                        self.stage = Field.DEFENDERS

            else:
                self.activeButton = False

        else:
            for i in range(len(self.players)):
                for j in range(i+1, len(self.players)):
                    p1 = self.players[i]
                    p2 = self.players[j]
                    if tools.dist(p1.x, p1.y, p2.x, p2.y) < 50:
                        p1vX = p1.vX
                        p1vY = p1.vY
                        p1.collide(p2.x, p2.y, p2.vX, p2.vY)
                        p2.collide(p1.x, p1.y, p1vX, p1vY)

            for player in self.players:
                player.x += player.vX * dt
                player.y += player.vY * dt

            for player in self.players:
                dir = math.atan2(player.vY, player.vX)+math.pi
                dX = math.cos(dir)*30*dt
                if abs(dX) > abs(player.vX):
                    dX = -player.vX

                dY = math.sin(dir)*30*dt
                if abs(dY) > abs(player.vY):
                    dY = -player.vY

                player.vX += dX
                player.vY += dY

            if self.time-self.gameStartTime > 2:
                self.ball.tick(dt, self.players)

            if 480 <= mousePos[0] <= 680 and 0 <= mousePos[1] <= 80:
                self.instructionsButtonHover = True
                if mouseClicked and not self.prevMouseClicked:
                    self.instructions = not self.instructions

            else:
                self.instructionsButtonHover = False


            if self.stage in [Field.ATTACKERS, Field.DEFENDERS]:
                if mousePos[0]<1:
                    camera.x -= 180 * dt

                if mousePos[0]>898:
                    camera.x += 180 * dt

                currActive = self.ball if self.ball.active else None
                if currActive is None:
                    for player in self.players:
                        if player.active:
                            currActive = player
                            break

                if currActive is None:
                    for player in self.players:
                        if player.team == self.selected:
                            player.tick(mousePos, mouseClicked, camera)

                    if self.selected == self.attacking:
                        self.ball.drag(mousePos, mouseClicked, camera)

                else:
                    if currActive == self.ball:
                        currActive.drag(mousePos, mouseClicked, camera)

                    else:
                        currActive.tick(mousePos, mouseClicked, camera)

                if 700 <= mousePos[0] <= 900 and 0 <= mousePos[1] <= 80:
                    self.activeButton = True
                    if mouseClicked and not self.prevMouseClicked:
                        if self.selected == self.attacking:
                            self.stage = Field.TRANSITION

                        else:
                            self.stage = Field.GAME
                            self.gameStartTime = self.time
                            self.released = False
                            self.ball.attachedPlayer = None
                            self.ball.invincible = 1

                        self.selected = 1-self.selected

                else:
                    self.activeButton = False

            if self.stage == Field.GAME:
                camera.x = self.ball.x-450
                camera.x = min(max(camera.x, -180), 1080)
                if self.time - self.gameStartTime > 2:
                    self.gameTime += dt
                    if not self.released:
                        self.released = True
                        self.release()

                    totalV = tools.dist(0, 0, self.ball.vX, self.ball.vY)
                    for player in self.players:
                        if 80 <= player.y <= 600 and -180 <= player.x <= 1980:
                            totalV += tools.dist(0, 0, player.vX, player.vY)

                    if totalV < 1 or not 80<=self.ball.y<=600 or not 0<=self.ball.x<=1800:
                        self.stage = Field.CUTSCENE
                        self.cutsceneStart = self.time
                        self.evaluated = False

            if self.stage == Field.CUTSCENE:
                if self.time - self.cutsceneStart > 3.5:
                    if self.gameTime > 180:
                        self.quarter += 1
                        self.gameTime = 0
                        self.leftteam = 1 - self.leftteam
                        self.lineofscrimmage = 1800-self.lineofscrimmage
                        self.firstdownline = 1800-self.firstdownline
                        if self.quarter == 3:
                            self.attacking = 1
                            self.lineofscrimmage = 1800-360
                            self.lineofscrimmage = 1800-540
                    self.stage = Field.TRANSITION
                    self.selected = self.attacking
                    self.make_players_default(center=self.lineofscrimmage, leftteam=self.leftteam, attackteam=self.attacking)
                    self.ball.plan = [0, 0]
                    self.ball.attachedPlayer = None
                    self.ball.vX = 0
                    self.ball.vY = 0
                    self.ball.x = self.lineofscrimmage - 180 if self.attacking == self.leftteam else self.lineofscrimmage + 180
                    self.ball.y = 360
                    camera.x = self.lineofscrimmage-450

                if not self.evaluated:
                    self.evaluated = True
                    control = -1
                    if self.ball.attachedPlayer is not None:
                        control = self.ball.attachedPlayer.team

                    if self.ball.x < 0:
                        if control == -1:
                            self.points[1-self.leftteam] += 3
                            self.message = "Field Goal!"
                            self.messageColor = (204, 10, 10) if 1-self.leftteam == 0 else (10, 139, 241)

                        else:
                            self.points[1-self.leftteam] += 7
                            self.message = "Touchdown!"
                            self.messageColor = (204, 10, 10) if 1-self.leftteam == 0 else (10, 139, 241)

                        self.attacking = 1 - self.attacking
                        self.lineofscrimmage = 360 if self.attacking == self.leftteam else 1440
                        if self.attacking == self.leftteam:
                            self.firstdownline = self.lineofscrimmage + 180

                        else:
                            self.firstdownline = self.lineofscrimmage - 180
                        self.down = 0
                        self.yards = 10

                    elif self.ball.x > 1800:
                        if control == -1:
                            self.points[self.leftteam] += 3
                            self.message = "Field Goal!"
                            self.messageColor = (204, 10, 10) if self.leftteam == 0 else (10, 139, 241)

                        else:
                            self.points[self.leftteam] += 7
                            self.message = "Touchdown!"
                            self.messageColor = (204, 10, 10) if self.leftteam == 0 else (10, 139, 241)

                        self.attacking = 1 - self.attacking
                        self.lineofscrimmage = 360 if self.attacking == self.leftteam else 1440
                        if self.attacking == self.leftteam:
                            self.firstdownline = self.lineofscrimmage + 180

                        else:
                            self.firstdownline = self.lineofscrimmage - 180
                        self.down = 0
                        self.yards = 10


                    elif not 80<=self.ball.y<=600:
                        if control == -1:
                            self.message = "Out of Bounds"
                            self.messageColor = (255, 255, 255)
                            self.down += 1
                            self.yards = round((abs(self.firstdownline-self.lineofscrimmage))/18)
                            if self.yards == 0:
                                self.yards = "Inches"

                            if not 0 < self.firstdownline < 1800:
                                self.yards = "Goal"

                            if self.down >= 4:
                                self.message = "Turnover"
                                self.messageColor = (255, 255, 255)
                                self.lineofscrimmage = self.ball.x
                                if self.attacking == self.leftteam:
                                    self.firstdownline = self.lineofscrimmage - 180

                                else:
                                    self.firstdownline = self.lineofscrimmage + 180

                                self.down = 0
                                self.yards = 10
                                self.attacking = 1-self.attacking

                        else:
                            if self.attacking != control:
                                self.message = "Turnover"
                                self.messageColor = (255, 255, 255)
                                self.lineofscrimmage = self.ball.x
                                if self.attacking == self.leftteam:
                                    self.firstdownline = self.lineofscrimmage - 180

                                else:
                                    self.firstdownline = self.lineofscrimmage + 180

                                self.down = 0
                                self.yards = 10
                                self.attacking = control

                            else:
                                if (self.attacking == self.leftteam and self.ball.x > self.firstdownline) or (self.attacking != self.leftteam and self.ball.x < self.firstdownline):
                                    self.message = "1st Down"
                                    self.messageColor = (255, 255, 255)
                                    self.lineofscrimmage = self.ball.x
                                    if self.attacking == self.leftteam:
                                        self.firstdownline = self.lineofscrimmage + 180

                                    else:
                                        self.firstdownline = self.lineofscrimmage - 180

                                    self.down = 0
                                    self.yards = 10
                                    self.attacking = control

                                else:
                                    self.down += 1
                                    self.yards = round((abs(self.firstdownline-self.ball.x))/18)
                                    if self.yards == 0:
                                        self.yards = "Inches"

                                    if not 0 < self.firstdownline < 1800:
                                        self.yards = "Goal"

                                    self.lineofscrimmage = self.ball.x
                                    self.message = f"{Field.down_to_words[self.down]} & {self.yards}"
                                    self.messageColor = (255, 255, 255)

                                    if self.down >= 4:
                                        self.message = "Turnover"
                                        self.messageColor = (255, 255, 255)
                                        self.lineofscrimmage = self.ball.x
                                        if self.attacking == self.leftteam:
                                            self.firstdownline = self.lineofscrimmage - 180

                                        else:
                                            self.firstdownline = self.lineofscrimmage + 180

                                        self.down = 0
                                        self.yards = 10
                                        self.attacking = 1-self.attacking

                    else:
                        if control == -1:
                            self.message = "Incomplete"
                            self.messageColor = (255, 255, 255)
                            self.down += 1
                            self.yards = round((abs(self.firstdownline-self.lineofscrimmage))/18)
                            if self.yards == 0:
                                self.yards = "Inches"

                            if not 0 < self.firstdownline < 1800:
                                self.yards = "Goal"

                            if self.down >= 4:
                                self.message = "Turnover"
                                self.messageColor = (255, 255, 255)
                                self.lineofscrimmage = self.ball.x
                                if self.attacking == self.leftteam:
                                    self.firstdownline = self.lineofscrimmage - 180

                                else:
                                    self.firstdownline = self.lineofscrimmage + 180

                                self.down = 0
                                self.yards = 10
                                self.attacking = 1-self.attacking

                        else:
                            if self.attacking != control:
                                self.message = "Turnover"
                                self.messageColor = (255, 255, 255)
                                self.lineofscrimmage = self.ball.x
                                if self.attacking == self.leftteam:
                                    self.firstdownline = self.lineofscrimmage - 180

                                else:
                                    self.firstdownline = self.lineofscrimmage + 180

                                self.down = 0
                                self.yards = 10
                                self.attacking = control

                            else:
                                if (self.attacking == self.leftteam and self.ball.x > self.firstdownline) or (self.attacking != self.leftteam and self.ball.x < self.firstdownline):
                                    self.message = "1st Down"
                                    self.messageColor = (255, 255, 255)
                                    self.lineofscrimmage = self.ball.x
                                    if self.attacking == self.leftteam:
                                        self.firstdownline = self.lineofscrimmage + 180

                                    else:
                                        self.firstdownline = self.lineofscrimmage - 180

                                    self.down = 0
                                    self.yards = 10
                                    self.attacking = control

                                else:
                                    self.down += 1
                                    self.yards = round((abs(self.firstdownline-self.ball.x))/18)
                                    if self.yards == 0:
                                        self.yards = "Inches"

                                    if not 0 < self.firstdownline < 1800:
                                        self.yards = "Goal"

                                    self.lineofscrimmage = self.ball.x
                                    self.message = f"{Field.down_to_words[self.down]} & {self.yards}"
                                    self.messageColor = (255, 255, 255)

                                    if self.down >= 4:
                                        self.message = "Turnover"
                                        self.messageColor = (255, 255, 255)
                                        self.lineofscrimmage = self.ball.x
                                        if self.attacking == self.leftteam:
                                            self.firstdownline = self.lineofscrimmage - 180

                                        else:
                                            self.firstdownline = self.lineofscrimmage + 180

                                        self.down = 0
                                        self.yards = 10
                                        self.attacking = 1-self.attacking

        self.prevMouseClicked = mouseClicked

    def blend(self, c1, c2, r):
        return [c1[0]*r+c2[0]*(1-r),
                c1[1]*r+c2[1]*(1-r),
                c1[2]*r+c2[2]*(1-r)]

    def render(self, screen, camera):
        if self.stage == Field.TRANSITION:
            nextUp = Text("Next Up", ("Courier", 80), (255, 255, 255), (0, 0))
            nextUp.centerAt(450, 200)
            nextUp.render(screen)
            team = Text("Red Team" if self.selected==0 else "Blue Team", ("Courier", 160), (204, 10, 10) if self.selected == 0 else (10, 139, 241), (0, 0))
            team.centerAt(450, 300)
            team.render(screen)
            attack = Text("Attackers" if self.attacking == self.selected else "Defenders", ("Courier", 100), (255, 255, 255), (0, 0))
            attack.centerAt(450, 400)
            attack.render(screen)

            pygame.draw.rect(screen, (42, 231, 0) if not self.activeButton else (24, 132, 0), pygame.Rect(350, 450, 200, 100), border_radius=20)
            st = Text("Start", ("Courier", 50), (0, 0, 0) if not self.activeButton else (255, 255, 255), (0, 0))
            st.centerAt(450, 500)
            st.render(screen)

        else:
            for i in range(10):
                pygame.draw.rect(screen, (38, 211, 0) if i%2==0 else (28, 154, 0), pygame.Rect(i*180-camera.x, 80-camera.y, 180, 520))
                if i != 0:
                    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(i*180-camera.x-5, 80-camera.y, 10, 520))
                    t = Text(f"{min(10*i, 100-10*i)}", ("Courier", 60), (255, 255, 255), 0, rotate=180)
                    t.centerAt(i*180-camera.x, 80-camera.y+80)
                    t.render(screen)
                    t = Text(f"{min(10*i, 100-10*i)}", ("Courier", 60), (255, 255, 255), 0)
                    t.centerAt(i*180-camera.x, 80-camera.y+520-80)
                    t.render(screen)

                    if i < 5:
                        pygame.draw.polygon(screen, (255, 255, 255), [(i*180-camera.x-40, 80-camera.y+80-10), (i*180-camera.x-40, 80-camera.y+80+10), (i*180-camera.x-70, 80-camera.y+80)])
                        pygame.draw.polygon(screen, (255, 255, 255), [(i*180-camera.x-40, 80-camera.y+520-80-10), (i*180-camera.x-40, 80-camera.y+520-80+10), (i*180-camera.x-70, 80-camera.y+520-80)])

                    elif i > 5:
                        pygame.draw.polygon(screen, (255, 255, 255), [(i*180-camera.x+40, 80-camera.y+80-10), (i*180-camera.x+40, 80-camera.y+80+10), (i*180-camera.x+70, 80-camera.y+80)])
                        pygame.draw.polygon(screen, (255, 255, 255), [(i*180-camera.x+40, 80-camera.y+520-80-10), (i*180-camera.x+40, 80-camera.y+520-80+10), (i*180-camera.x+70, 80-camera.y+520-80)])


                pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(i*180-camera.x+90-2, 80-camera.y, 4, 520))
                for j in list(range(1, 5))+list(range(6, 10)):
                    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(i*180+j*18-camera.x-1, 80-camera.y+30, 2, 20))
                    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(i*180+j*18-camera.x-1, 80-camera.y+520-50, 2, 20))
                    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(i*180+j*18-camera.x-1, 80-camera.y+163, 2, 20))
                    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(i*180+j*18-camera.x-1, 80-camera.y+520-173-10, 2, 20))

                pygame.draw.rect(screen, (194, 0, 0), pygame.Rect(-180-camera.x, 80-camera.y, 180, 520))
                pygame.draw.rect(screen, (0, 129, 231), pygame.Rect(1800-camera.x, 80-camera.y, 180, 520))

            pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(self.lineofscrimmage-camera.x-6, 80-camera.y, 12, 520))
            if 0 < self.firstdownline < 1800:
                pygame.draw.rect(screen, (255, 255, 50), pygame.Rect(self.firstdownline-camera.x-6, 80-camera.y, 12, 520))

            currActive = self.ball if self.ball.active else None
            if currActive is None:
                for player in self.players:
                    if player.active:
                        currActive = player
                        break

            for player in self.players:
                if self.stage in [Field.ATTACKERS, Field.DEFENDERS]:
                    if currActive is None:
                        if player.team == self.selected:
                            pygame.draw.circle(screen, (250, 255, 80), (player.x-camera.x, player.y-camera.y), 35+5*math.sin(math.radians(self.time*360%360)))

                    else:
                        if currActive == player:
                            pygame.draw.circle(screen, (250, 255, 80), (player.x-camera.x, player.y-camera.y), 40)

                pygame.draw.circle(screen, (0, 0, 0), (player.x-camera.x, player.y-camera.y), 25)
                pygame.draw.circle(screen, (204, 10, 10) if player.team == 0 else (10, 139, 241), (player.x-camera.x, player.y-camera.y), 20)

            if self.stage in [Field.ATTACKERS, Field.DEFENDERS]:
                if currActive is None:
                    if self.selected == self.attacking:
                        pygame.draw.circle(screen, (250, 255, 80), (self.ball.x-camera.x, self.ball.y-camera.y), 23+5*math.sin(math.radians(self.time*360%360)))
                else:
                    if currActive == self.ball:
                        pygame.draw.circle(screen, (250, 255, 80), (self.ball.x-camera.x, self.ball.y-camera.y), 28)

            if self.stage == Field.GAME:
                if self.ball.invincible > 0:
                    pygame.draw.circle(screen, (250, 255, 80), (self.ball.x-camera.x, self.ball.y-camera.y), 18)

            pts = [[-15, 0],
                   [-10, 5],
                   [-5, 8],
                   [0, 10],
                   [5, 8],
                   [10, 5],
                   [15, 0]]

            ext = []
            for pt in pts:
                ext.append([pt[0], -pt[1]])

            pts.extend(ext)

            for pt in pts:
                pt[0] += self.ball.x-camera.x
                pt[1] += self.ball.y-camera.y

            pygame.draw.polygon(screen, (171, 99, 0), pts)

            for player in self.players:
                if self.stage == Field.ATTACKERS:
                    showIf = self.attacking

                else:
                    showIf = 1-self.attacking

                if showIf == player.team or self.stage == Field.GAME:
                    if player.plan != [0, 0]:
                        arrow = [(player.x-camera.x, player.y-camera.y),

                                 (player.x-camera.x+player.plan[0]*0.9*math.cos(player.plan[1])+0.05*player.plan[0]*math.cos(player.plan[1]-math.pi/2),
                                  player.y-camera.y+player.plan[0]*0.9*math.sin(player.plan[1])+0.05*player.plan[0]*math.sin(player.plan[1]-math.pi/2)),

                                 (player.x-camera.x+player.plan[0]*0.9*math.cos(player.plan[1])+0.1*player.plan[0]*math.cos(player.plan[1]-math.pi/2),
                                  player.y-camera.y+player.plan[0]*0.9*math.sin(player.plan[1])+0.1*player.plan[0]*math.sin(player.plan[1]-math.pi/2)),

                                 (player.x-camera.x+player.plan[0]*math.cos(player.plan[1]), player.y-camera.y+player.plan[0]*math.sin(player.plan[1])),

                                 (player.x-camera.x+player.plan[0]*0.9*math.cos(player.plan[1])+0.1*player.plan[0]*math.cos(player.plan[1]+math.pi/2),
                                  player.y-camera.y+player.plan[0]*0.9*math.sin(player.plan[1])+0.1*player.plan[0]*math.sin(player.plan[1]+math.pi/2)),

                                 (player.x-camera.x+player.plan[0]*0.9*math.cos(player.plan[1])+0.05*player.plan[0]*math.cos(player.plan[1]+math.pi/2),
                                  player.y-camera.y+player.plan[0]*0.9*math.sin(player.plan[1])+0.05*player.plan[0]*math.sin(player.plan[1]+math.pi/2)),]
                        if self.stage == Field.GAME:
                            pygame.draw.polygon(screen, (204, 10, 10) if player.team == 0 else (10, 139, 241), arrow)
                            pygame.draw.polygon(screen, (0, 0, 0), arrow, width=3)

                        else:
                            pygame.draw.polygon(screen, self.blend((255, 251, 0), (255, 67, 67), 1-player.plan[0]/540), arrow)

            if self.stage == Field.DEFENDERS:
                avgX = 0
                avgY = 0
                avgvX = 0
                avgvY = 0
                num=0
                for player in self.players:
                    if player.team == self.attacking:
                        if player.plan != [0, 0]:
                            avgX += player.x
                            avgY += player.y
                            avgvX += player.plan[0]*math.cos(player.plan[1])
                            avgvY += player.plan[0]*math.sin(player.plan[1])
                            num+=1
                avgx=0
                avgy=0
                avgplan=[0, 0]
                if num != 0:
                    avgx = avgX/num
                    avgy = avgY/num
                    avgvX /= num
                    avgvY /= num
                    avgplan = [tools.dist(0, 0, avgvX, avgvY), math.atan2(avgvY, avgvX)]


                arrow = [(avgx-camera.x, avgy-camera.y),

                         (avgx-camera.x+avgplan[0]*0.9*math.cos(avgplan[1])+0.05*avgplan[0]*math.cos(avgplan[1]-math.pi/2),
                          avgy-camera.y+avgplan[0]*0.9*math.sin(avgplan[1])+0.05*avgplan[0]*math.sin(avgplan[1]-math.pi/2)),

                         (avgx-camera.x+avgplan[0]*0.9*math.cos(avgplan[1])+0.1*avgplan[0]*math.cos(avgplan[1]-math.pi/2),
                          avgy-camera.y+avgplan[0]*0.9*math.sin(avgplan[1])+0.1*avgplan[0]*math.sin(avgplan[1]-math.pi/2)),

                         (avgx-camera.x+avgplan[0]*math.cos(avgplan[1]), avgy-camera.y+avgplan[0]*math.sin(avgplan[1])),

                         (avgx-camera.x+avgplan[0]*0.9*math.cos(avgplan[1])+0.1*avgplan[0]*math.cos(avgplan[1]+math.pi/2),
                          avgy-camera.y+avgplan[0]*0.9*math.sin(avgplan[1])+0.1*avgplan[0]*math.sin(avgplan[1]+math.pi/2)),

                         (avgx-camera.x+avgplan[0]*0.9*math.cos(avgplan[1])+0.05*avgplan[0]*math.cos(avgplan[1]+math.pi/2),
                          avgy-camera.y+avgplan[0]*0.9*math.sin(avgplan[1])+0.05*avgplan[0]*math.sin(avgplan[1]+math.pi/2)),]

                pygame.draw.polygon(screen, self.blend((255, 251, 0), (255, 67, 67), 1-avgplan[0]/540), arrow)

            arrow = [(self.ball.x-camera.x, self.ball.y-camera.y),

                     (self.ball.x-camera.x+self.ball.plan[0]*0.9*math.cos(self.ball.plan[1])+0.05*self.ball.plan[0]*math.cos(self.ball.plan[1]-math.pi/2),
                      self.ball.y-camera.y+self.ball.plan[0]*0.9*math.sin(self.ball.plan[1])+0.05*self.ball.plan[0]*math.sin(self.ball.plan[1]-math.pi/2)),

                     (self.ball.x-camera.x+self.ball.plan[0]*0.9*math.cos(self.ball.plan[1])+0.1*self.ball.plan[0]*math.cos(self.ball.plan[1]-math.pi/2),
                      self.ball.y-camera.y+self.ball.plan[0]*0.9*math.sin(self.ball.plan[1])+0.1*self.ball.plan[0]*math.sin(self.ball.plan[1]-math.pi/2)),

                     (self.ball.x-camera.x+self.ball.plan[0]*math.cos(self.ball.plan[1]), self.ball.y-camera.y+self.ball.plan[0]*math.sin(self.ball.plan[1])),

                     (self.ball.x-camera.x+self.ball.plan[0]*0.9*math.cos(self.ball.plan[1])+0.1*self.ball.plan[0]*math.cos(self.ball.plan[1]+math.pi/2),
                      self.ball.y-camera.y+self.ball.plan[0]*0.9*math.sin(self.ball.plan[1])+0.1*self.ball.plan[0]*math.sin(self.ball.plan[1]+math.pi/2)),

                     (self.ball.x-camera.x+self.ball.plan[0]*0.9*math.cos(self.ball.plan[1])+0.05*self.ball.plan[0]*math.cos(self.ball.plan[1]+math.pi/2),
                      self.ball.y-camera.y+self.ball.plan[0]*0.9*math.sin(self.ball.plan[1])+0.05*self.ball.plan[0]*math.sin(self.ball.plan[1]+math.pi/2)),]

            if self.stage == Field.GAME:
                pygame.draw.polygon(screen, (91, 63, 0), arrow)
                pygame.draw.polygon(screen, (0, 0, 0), arrow, width=3)

            elif self.stage == Field.ATTACKERS:
                pygame.draw.polygon(screen, self.blend((255, 251, 0), (255, 67, 67), 1-self.ball.plan[0]/540), arrow)

            if self.stage == Field.CUTSCENE:
                if 1<=self.time-self.cutsceneStart<=3:
                    surf = pygame.Surface((900, 150))
                    surf.set_alpha(200)
                    surf.fill((0, 0, 0))
                    screen.blit(surf, (0, 265))
                    msg = Text(self.message, ("Courier", 100), self.messageColor, (0, 0))
                    msg.centerAt(450, 315)
                    msg.render(screen)

                    timeMsg = ""
                    if self.gameTime > 180:
                        if self.quarter != 4:
                            timeMsg = f"{Field.down_to_words[self.quarter]} Quarter Ended"

                        else:
                            timeMsg = f"Game Ended"

                    else:
                        minutes = round((180-self.gameTime)//60)
                        seconds = math.floor((180-self.gameTime)%60)
                        timeMsg = f"{minutes}:{'' if seconds>=10 else '0'}{seconds}"
                    quart = Text(timeMsg, ("Courier", 40), (255, 255, 255), (0, 0))
                    quart.centerAt(450, 390)
                    quart.render(screen)

            # (204, 10, 10) if player.team == 0 else (10, 139, 241)
            pygame.draw.rect(screen, (92, 61, 0), pygame.Rect(0, 0, 900, 80))
            pygame.draw.rect(screen, (204, 10, 10), pygame.Rect(0, 0, 260, 40), border_radius=10)
            pygame.draw.rect(screen, (10, 139, 241), pygame.Rect(0, 40, 260, 40), border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(210, 0, 50, 40), border_radius=10)
            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(210, 40, 50, 40), border_radius=10)
            Text("Red Team", ("Courier", 35), (128, 0, 0), (5, 0), bold=True).render(screen)
            Text("Blue Team", ("Courier", 35), (7, 78, 134), (5, 40), bold=True).render(screen)
            Text(str(self.points[0]), ("Courier", 35), (0, 0, 0), (215, 0), bold=True).render(screen)
            Text(str(self.points[1]), ("Courier", 35), (0, 0, 0), (215, 40), bold=True).render(screen)

            Text(f"{Field.down_to_words[self.down]} & {self.yards}", ("Courier", 35), (255, 255, 0), (280, 0), bold=True).render(screen)
            minutes = max(round((180-self.gameTime)//60), 0)
            seconds = max(math.floor((180-self.gameTime)%60), 0)
            if self.gameTime >= 180:
                seconds = 0
            Text(f"Q{self.quarter+1} {minutes}:{'' if seconds>=10 else '0'}{seconds}", ("Courier", 35), (255, 255, 255), (280, 40), bold=True).render(screen)

            if self.stage in [Field.ATTACKERS, Field.DEFENDERS]:
                ftButtonColor = (42, 231, 0) if not self.activeButton else (24, 132, 0)
            else:
                ftButtonColor = (120, 120, 120)

            pygame.draw.rect(screen, ftButtonColor, pygame.Rect(700, 0, 200, 80), border_radius=10)
            ft = Text("Finish\nTurn", ("Courier", 40), (255, 255, 255), (0, 0), bold=True)
            ft.centerAt(800, 40)
            ft.render(screen)

            pygame.draw.rect(screen, (0, 28, 98) if self.instructionsButtonHover else (41, 83, 186), pygame.Rect(480, 0, 200, 80), border_radius=10)
            ft = Text("Toggle\nHelp", ("Courier", 40), (255, 255, 255), (0, 0), bold=True)
            ft.centerAt(580, 40)
            ft.render(screen)

            if self.instructions:
                if self.stage in [Field.ATTACKERS, Field.DEFENDERS]:
                    if self.stage == Field.ATTACKERS:
                        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, 80, 900, 40))
                        Text("You are attacking! Charge towards the opponent's side to get past the yellow line, or get to the \nendzone!", ("Courier", 15), (0, 0, 0), (5, 80), bold=True).render(screen)

                    else:
                        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, 80, 900, 40))
                        Text("You are defending! Try and stop the opponent from getting further into your territory!", ("Courier", 15), (0, 0, 0), (5, 80), bold=True).render(screen)
                        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(280, 400, 200, 60))
                        Text("This arrow represents\nthe average attack of \nthe opponent.", ("Courier", 15), (0, 0, 0), (285, 400),bold=True).render(screen)


                    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(10, 500, 300, 80))
                    Text("Move your mouse towards the ends \nof the field to move the camera \nthat way.", ("Courier", 15), (0, 0, 0), (15, 500), bold=True).render(screen)

                    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(500, 300, 300, 250))
                    Text("Pull and drag on the pulsating \norbs to set the strenth and \ndirection of their movement.\nOnce they move, they'll bump \ninto other orbs or catch the \nball after its invincibility \nperiod.\n\nThe football (the brown ball)\n will start the game \nwith 1 second of invincibility. \nIt doesn't bump into others, \nbut can be caught if \nclose to another player.", ("Courier", 15), (0, 0, 0), (505, 300), bold=True).render(screen)

                else:
                    if self.stage == Field.GAME:
                        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, 80, 900, 40))
                        Text("Sit back and relax, and watch the game play out. Or maybe not relax - you got a game to win!", ("Courier", 15), (0, 0, 0), (5, 80), bold=True).render(screen)


                    else:
                        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, 80, 900, 40))
                        Text("The big text is the referee's ruling. The smaller text below is the time remaining in the quarter.\nGet ready for the next round!", ("Courier", 15), (0, 0, 0), (5, 80), bold=True).render(screen)
