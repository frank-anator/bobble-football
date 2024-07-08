import pygame

from camera import Camera
from fakefield import FakeField
from field import Field
from text import Text

pygame.init()
screen = pygame.display.set_mode((900, 600), pygame.SCALED|pygame.FULLSCREEN, vsync=1)
clock = pygame.time.Clock()

camera = Camera(0, 0)
field = Field()
fakefield = FakeField()

screenID = 0
prevMouseClicked = False
points = [0, 0]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    keys = pygame.key.get_pressed()
    dt = clock.get_time()/1000
    mouseClicked = pygame.mouse.get_pressed()[0]
    mousePos = pygame.mouse.get_pos()

    if screenID == 0:
        fakefield.tick(mousePos, dt)
        fakefield.render(screen)

        surf = pygame.Surface((900, 600), pygame.SRCALPHA)
        surf.fill((255, 255, 255))
        surf.set_alpha(60)
        screen.blit(surf, (0, 0))

        Text("Bobble", ("Courier", 100), (204, 10, 10), (150, 100), bold=True).render(screen)
        Text("Football", ("Courier", 100), (10, 139, 241), (350, 200), bold=True).render(screen)

        if 250 <= mousePos[0] <= 650 and 350 <= mousePos[1] <= 500:
            pygame.draw.rect(screen, (255, 205, 0), pygame.Rect(250, 350, 400, 150), border_radius=10)
            if mouseClicked and not prevMouseClicked:
                screenID = 1
        else:
            pygame.draw.rect(screen, (187, 150, 0), pygame.Rect(250, 350, 400, 150), border_radius=10)

        pT = Text("Play!", ("Courier", 80), (0, 0, 0), (350, 200), bold=True)
        pT.centerAt(450, 425)
        pT.render(screen)

    elif screenID == 1:
        field.tick(mousePos, mouseClicked, camera, dt)
        field.render(screen, camera)
        if field.quarter >= 4:
            points = field.points
            screenID = 2
            field = Field()

    else:
        fakefield.tick(mousePos, dt)
        fakefield.render(screen)

        surf = pygame.Surface((900, 600), pygame.SRCALPHA)
        surf.fill((255, 255, 255))
        surf.set_alpha(60)
        screen.blit(surf, (0, 0))

        r = Text(str(points[0]), ("Courier", 60), (204, 10, 10), (150, 100), bold=True)
        b = Text(str(points[1]), ("Courier", 60), (10, 139, 241), (350, 100), bold=True)
        r.centerAt(400, 200)
        b.centerAt(500, 200)
        r.render(screen)
        b.render(screen)
        if points[0] > points[1]:
            w = Text("Red Wins!", ("Courier", 120), (255, 0, 0), (0, 0), bold=True)

        elif points[0] < points[1]:
            w = Text("Blue Wins!", ("Courier", 120), (0, 0, 255), (0, 0), bold=True)

        else:
            w = Text("Tie!", ("Courier", 120), (0, 0, 0), (0, 0), bold=True)

        w.centerAt(450, 300)
        w.render(screen)

        if 200 <= mousePos[0] <= 700 and 450 <= mousePos[1] <= 570:
            pygame.draw.rect(screen, (255, 205, 0), pygame.Rect(200, 450, 500, 120), border_radius=10)
            if mouseClicked and not prevMouseClicked:
                screenID = 1
        else:
            pygame.draw.rect(screen, (187, 150, 0), pygame.Rect(200, 450, 500, 120), border_radius=10)

        pT = Text("Play again", ("Courier", 80), (0, 0, 0), (450, 200), bold=True)
        pT.centerAt(450, 510)
        pT.render(screen)

    prevMouseClicked = mouseClicked

    pygame.display.flip()
    clock.tick()

pygame.quit()
