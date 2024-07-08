import math
import random

import pygame.draw

import tools
from camera import Camera
from player import Player
from text import Text


class FakeField:
    def __init__(self):
        self.players = []
        self.make_players_default()
        self.camera = Camera(450, 0)



    def make_players_default(self, center=900, leftteam=0):
        self.players = []
        for i in range(50, 600, 75):
            self.players.append(Player(center-90, i, leftteam))
            self.players.append(Player(center+90, i, 1-leftteam))
            self.players.append(Player(center-180, i, leftteam))
            self.players.append(Player(center+180, i, 1-leftteam))


    def tick(self, mousePos, dt):
        self.camera.x = mousePos[0] * (1260/900) -180
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
            if player.x < 0:
                player.x = 0
                player.vX *= -1

            if player.x > 1800:
                player.x = 1800
                player.vX *= -1

            if player.y < 0:
                player.y = 0
                player.vY *= -1

            if player.y > 600:
                player.y = 600
                player.vY *= -1


        for player in self.players:
            player.vX += random.randint(-10, 10)
            player.vY += random.randint(-10, 10)
            player.vX = max(min(player.vX, 300), -300)
            player.vY = max(min(player.vY, 300), -300)


    def render(self, screen):
        camera = self.camera
        for i in range(10):
            pygame.draw.rect(screen, (38, 211, 0) if i%2==0 else (28, 154, 0), pygame.Rect(i*180-camera.x, camera.y, 180, 600))
            if i != 0:
                pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(i*180-camera.x-5, camera.y, 10, 600))
                t = Text(f"{min(10*i, 100-10*i)}", ("Courier", 60), (255, 255, 255), 0, rotate=180)
                t.centerAt(i*180-camera.x, camera.y+80)
                t.render(screen)
                t = Text(f"{min(10*i, 100-10*i)}", ("Courier", 60), (255, 255, 255), 0)
                t.centerAt(i*180-camera.x, camera.y+600-80)
                t.render(screen)

                if i < 5:
                    pygame.draw.polygon(screen, (255, 255, 255), [(i*180-camera.x-40, camera.y+80-10), (i*180-camera.x-40, camera.y+80+10), (i*180-camera.x-70, camera.y+80)])
                    pygame.draw.polygon(screen, (255, 255, 255), [(i*180-camera.x-40, camera.y+600-80-10), (i*180-camera.x-40, camera.y+600-80+10), (i*180-camera.x-70, camera.y+600-80)])

                elif i > 5:
                    pygame.draw.polygon(screen, (255, 255, 255), [(i*180-camera.x+40, camera.y+80-10), (i*180-camera.x+40, camera.y+80+10), (i*180-camera.x+70, camera.y+80)])
                    pygame.draw.polygon(screen, (255, 255, 255), [(i*180-camera.x+40, camera.y+600-80-10), (i*180-camera.x+40, camera.y+600-80+10), (i*180-camera.x+70, camera.y+600-80)])


            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(i*180-camera.x+90-2, camera.y, 4, 600))
            for j in list(range(1, 5))+list(range(6, 10)):
                pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(i*180+j*18-camera.x-1, camera.y+30, 2, 20))
                pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(i*180+j*18-camera.x-1, camera.y+600-50, 2, 20))
                pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(i*180+j*18-camera.x-1, camera.y+163, 2, 20))
                pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(i*180+j*18-camera.x-1, camera.y+600-173-10, 2, 20))

            pygame.draw.rect(screen, (194, 0, 0), pygame.Rect(-180-camera.x, camera.y, 180, 600))
            pygame.draw.rect(screen, (0, 129, 231), pygame.Rect(1800-camera.x, camera.y, 180, 600))


        for player in self.players:
            pygame.draw.circle(screen, (0, 0, 0), (player.x-camera.x, player.y-camera.y), 25)
            pygame.draw.circle(screen, (204, 10, 10) if player.team == 0 else (10, 139, 241), (player.x-camera.x, player.y-camera.y), 20)