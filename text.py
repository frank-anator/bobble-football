import pygame

class Text: # allows for renderable text
    def __init__(self, text, font, color, pos, outline=0, outline_color=None, rotate=0, bold=False):
        self.font_render = None
        self.text = text
        self.font = font
        self.color = color
        self.pos = pos
        self.w = 0
        self.h = 0
        self.outline = outline
        self.outline_render = None
        self.outline_color = outline_color
        self.rotate = rotate
        self.bold = bold
        self.make_font()

    def centerAt(self, x, y):
        self.pos = (x-self.w/2, y-self.h/2)

    def set_text(self, newtext):
        if self.text != newtext:
            self.text = newtext
            self.make_font()

    def set_color(self, newColor):
        self.color = newColor
        self.make_font()

    def make_font(self):
        font = self.font[0]
        if not isinstance(self.font[0], pygame.font.Font):
            font = pygame.font.SysFont(self.font[0], self.font[1], bold=self.bold)


        if "\n" in self.text:
            texts = self.text.split("\n")
            self.font_render = []
            maxW = 0
            for text in texts:
                this_render = font.render(text, True, self.color, None)
                if self.rotate != 0:
                    this_render = pygame.transform.rotate(this_render, self.rotate)
                self.font_render.append(this_render)
                if self.font_render[-1].get_width() > maxW:
                    maxW = self.font_render[-1].get_width()
            self.w = maxW
            self.h = (len(texts)-1) * (self.font[1] + 2) + self.font_render[-1].get_height()

        else:
            self.font_render = font.render(self.text, True, self.color, None)
            if self.rotate != 0:
                self.font_render = pygame.transform.rotate(self.font_render, self.rotate)
            self.w = self.font_render.get_width()
            self.h = self.font_render.get_height()

        if self.outline > 0:
            if type(self.font_render) != list:
                mask = pygame.mask.from_surface(self.font_render)
                self.outline_render = pygame.Surface((self.font_render.get_width()+self.outline*4, self.font_render.get_height()+self.outline*4), pygame.SRCALPHA)
                for x, y in mask.outline():
                    for xO in range(self.outline):
                        for yO in range(self.outline):
                            self.outline_render.set_at((self.outline*2+x+xO, self.outline*2+y+yO), self.outline_color)

            else:
                self.outline_render = []
                for text in self.font_render:
                    mask = pygame.mask.from_surface(text)
                    self.outline_render.append(pygame.Surface((text.get_width()+self.outline*4, text.get_height()+self.outline*4), pygame.SRCALPHA))
                    for x, y in mask.outline():
                        for xO in range(-round(self.outline)/2, round(self.outline/2)+1):
                            for yO in range(-round(self.outline)/2, round(self.outline/2)+1):
                                self.outline_render[-1].set_at((self.outline*2+x+xO, self.outline*2+y+yO), self.outline_color)


    def render(self, screen):
        if type(self.font_render) != list:
            if self.outline > 0:
                screen.blit(self.outline_render, (self.pos[0]-self.outline*2, self.pos[1]-self.outline*2))
            screen.blit(self.font_render, self.pos)


        else:
            for index, render in enumerate(self.font_render):
                if self.outline > 0:
                    screen.blit(self.outline_render[index], (self.pos[0]-self.outline*2, self.pos[1]+ index * (self.font[1] + 2)-self.outline*2))
                screen.blit(render, (self.pos[0], self.pos[1] + index * (self.font[1] + 2)))
