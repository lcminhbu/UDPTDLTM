import pygame

class Object():
    def __init__(self,vitri,image,vantoc):
        self.vitri=vitri
        self.vantoc=vantoc
        self.image=pygame.image.load(image)
class Player(Object):
    def __init__(self,huong,vitri,vantoc=5,diem=0,image="assets/paddle.png"):
        super().__init__(vitri,image,vantoc)
        self.huong=huong
        self.diem=diem
class Ball(Object):
    def __init__(self, vitri, image="assets/ball.png"):
        super().__init__( vitri, image, [3,3])
    def dichuyen(self):
        self.vitri[0] += self.vantoc[0]
        self.vitri[1] += self.vantoc[1]
    def reset(self):
        self.vitri[0]=285
        self.vitri[1]=300
class Map():
    def __init__(self, clock):
        pygame.init()
        self.winner=""
        self.tick_time=clock
        self.clock = pygame.time.Clock()
        self.SIZE = (600, 600)
        self.canvas = pygame.display.set_mode(self.SIZE)
        self.BG_COLOR = (70,95,70)
        self.p1=Player(True,[0,250])
        self.p2=Player(True,[570,250])
        self.ball=Ball([285,300])
        self.loop=True
        self.w_pressed=False
        self.s_pressed=False
        self.up_pressed=False
        self.down_pressed=False
        self.font = pygame.font.Font("freesansbold.ttf",20)
    def inra(self):
        p1_text = self.font.render(str(self.p1.diem), False, (255,255,255))
        p2_text = self.font.render(str(self.p2.diem), False, (255,255,255))
        winner_text= self.font.render(self.winner, False, (255,255,255))
        self.canvas.fill(self.BG_COLOR)
        self.canvas.blit(self.p1.image, self.p1.vitri)
        self.canvas.blit(self.p2.image, self.p2.vitri)
        self.canvas.blit(self.ball.image, self.ball.vitri)
        self.canvas.blit(p1_text, (285, 20))
        self.canvas.blit(p2_text, (325, 20))
        self.canvas.blit(winner_text, (265, 300))
    def ballcheck(self):
        if self.p1.vitri[1] <= self.ball.vitri[1] <= (self.p1.vitri[1] + 120) and self.ball.vitri[0] <=  (self.p1.vitri[0] + 30):
            self.ball.vantoc[0] = -self.ball.vantoc[0]
        if self.p2.vitri[1] <= self.ball.vitri[1] <= (self.p2.vitri[1] + 120) and self.ball.vitri[0] >=  (self.p2.vitri[0] -20):
            self.ball.vantoc[0] = - self.ball.vantoc[0]
        if self.ball.vitri[0] <= 0:
            self.ball.vantoc[0] = -self.ball.vantoc[0]
            self.p2.diem+=1
        if self.ball.vitri[0] >= 580:
            self.ball.vantoc[0] = -self.ball.vantoc[0]
            self.p1.diem+=1
        if self.ball.vitri[1] <= 0 or self.ball.vitri[1] >= 580:
            self.ball.vantoc[1] = -self.ball.vantoc[1]
    def paddledichuyen(self):
        if self.w_pressed:
            self.p1.vitri[1] -= self.p1.vantoc
        elif self.s_pressed:
            self.p1.vitri[1] += self.p1.vantoc
        elif self.up_pressed:
            self.p2.vitri[1] -= self.p2.vantoc
        elif self.down_pressed:
            self.p2.vitri[1] += self.p2.vantoc
    def tinhdiem(self):
        if self.p1.diem >= 5:
            self.winner = "Player 1 win"
            return False
        if self.p2.diem >= 5:
            self.winner = "Player 2 win"
            return False
        return True
    def manchoichinh(self):
        pygame.display.set_caption("ponggame version 2 ")
        while self.loop:
            self.ballcheck()
            self.ball.dichuyen()
            is_end_game = self.tinhdiem()
            if is_end_game==True:
                events = pygame.event.get()
                for e in events:
                    if e.type == pygame.QUIT:
                        self.loop = False
            else:
                events = pygame.event.get()
                for e in events:
                    if e.type == pygame.QUIT:
                        self.loop = False
                    elif e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_w:
                            self.w_pressed = True
                        elif e.key == pygame.K_s:
                            self.s_pressed = True
                        elif e.key == pygame.K_UP:
                            self.up_pressed = True
                        elif e.key == pygame.K_DOWN:
                            self.down_pressed = True
                    elif e.type == pygame.KEYUP:
                        if  e.key == pygame.K_w:
                            self.w_pressed = False
                        elif e.key == pygame.K_s:
                            self.s_pressed = False
                        elif e.key == pygame.K_DOWN:
                            self.down_pressed = False
                        elif e.key == pygame.K_UP:
                            self.up_pressed = False
                if self.p1.vitri[1] <= 0:
                        self.w_pressed = False
                if self.p2.vitri[1] <= 0:
                        self.up_pressed = False
                if self.p1.vitri[1] >= 480:
                        self.s_pressed = False
                if self.p2.vitri[1] >= 480:
                        self.down_pressed = False
                self.paddledichuyen()
            self.inra()
            self.clock.tick(self.tick_time)
            pygame.display.flip()
a=Map(60)
a.manchoichinh()