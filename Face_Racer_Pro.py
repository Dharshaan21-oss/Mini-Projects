
import pygame
import cv2
import random
import math
import sys

WIDTH, HEIGHT = 1000, 700
ROAD_WIDTH = 500
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Face Racer Pro")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 28)
big_font = pygame.font.SysFont("arial", 72)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-6, 6)
        self.vy = random.uniform(-6, 6)
        self.life = random.randint(20, 50)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 150, 0), (int(self.x), int(self.y)), 3)

class Player:
    def __init__(self):
        self.x = WIDTH // 2 - 30
        self.y = HEIGHT - 140
        self.w = 60
        self.h = 110

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 120, 255), self.rect, border_radius=10)
        pygame.draw.rect(screen, (220,220,255), (self.x+10,self.y+15,40,20))

class Enemy:
    COLORS = [(255,0,0),(255,120,0),(255,0,255),(255,255,0)]
    def __init__(self, road_x):
        lane = random.choice([0,1,2])
        self.x = road_x + 70 + lane * 140
        self.y = -150
        self.w = 60
        self.h = random.choice([90,110,130])
        self.color = random.choice(self.COLORS)

    @property
    def rect(self):
        return pygame.Rect(self.x,self.y,self.w,self.h)

    def update(self,speed):
        self.y += speed

    def draw(self,screen):
        pygame.draw.rect(screen,self.color,self.rect,border_radius=8)

class FaceController:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def get_direction(self):
        ret, frame = self.cap.read()
        if not ret:
            return "center", None

        frame = cv2.flip(frame,1)
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray,1.1,5)

        direction = "center"

        if len(faces):
            x,y,w,h = faces[0]
            center = x + w//2
            mid = frame.shape[1]//2

            if center < mid - 60:
                direction = "left"
            elif center > mid + 60:
                direction = "right"

            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)

        return direction, frame

    def close(self):
        self.cap.release()

class Game:
    def __init__(self):
        self.road_x = (WIDTH - ROAD_WIDTH)//2
        self.player = Player()
        self.face = FaceController()
        self.enemies = []
        self.particles = []
        self.score = 0
        self.high_score = 0
        self.speed = 7
        self.spawn_timer = 0
        self.line_offset = 0
        self.state = "menu"
        self.weather = "clear"
        self.weather_timer = 0

    def reset(self):
        self.player = Player()
        self.enemies.clear()
        self.particles.clear()
        self.score = 0
        self.speed = 7
        self.state = "playing"

    def update_weather(self):
        self.weather_timer += 1
        if self.weather_timer > 900:
            self.weather_timer = 0
            self.weather = random.choice(["clear","rain","fog"])

    def spawn_enemy(self):
        self.enemies.append(Enemy(self.road_x))

    def draw_road(self):
        pygame.draw.rect(screen,(60,60,60),(self.road_x,0,ROAD_WIDTH,HEIGHT))

        self.line_offset += self.speed
        if self.line_offset > 60:
            self.line_offset = 0

        for y in range(-60,HEIGHT,100):
            pygame.draw.rect(screen,(255,255,255),
                             (WIDTH//2-5,y+self.line_offset,10,50))

    def draw_weather(self):
        if self.weather == "rain":
            for _ in range(70):
                x = random.randint(0,WIDTH)
                y = random.randint(0,HEIGHT)
                pygame.draw.line(screen,(180,180,255),(x,y),(x+3,y+10),1)

        elif self.weather == "fog":
            fog = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
            fog.fill((200,200,200,70))
            screen.blit(fog,(0,0))

    def explosion(self):
        for _ in range(100):
            self.particles.append(
                Particle(self.player.x+30,self.player.y+50)
            )

    def update_playing(self):
        direction, frame = self.face.get_direction()

        if direction == "left":
            self.player.x -= 8
        elif direction == "right":
            self.player.x += 8

        self.player.x = max(
            self.road_x+10,
            min(self.player.x,self.road_x+ROAD_WIDTH-self.player.w-10)
        )

        self.spawn_timer += 1

        if self.spawn_timer > max(18,50-self.speed):
            self.spawn_enemy()
            self.spawn_timer = 0

        for enemy in self.enemies:
            enemy.update(self.speed)

            if enemy.rect.colliderect(self.player.rect):
                self.explosion()
                self.high_score = max(self.high_score,self.score)
                self.state = "gameover"

        self.enemies = [e for e in self.enemies if e.y < HEIGHT+150]

        self.score += 1

        if self.score % 500 == 0:
            self.speed += 1

        self.update_weather()

        if frame is not None:
            frame = cv2.resize(frame,(260,180))
            cv2.imshow("Face Camera",frame)
            cv2.waitKey(1)

    def draw_hud(self):
        screen.blit(font.render(f"Score: {self.score}",True,(255,255,255)),(20,20))
        screen.blit(font.render(f"High Score: {self.high_score}",True,(255,255,255)),(20,55))
        screen.blit(font.render(f"Speed: {self.speed}",True,(255,255,255)),(20,90))
        screen.blit(font.render(f"Weather: {self.weather}",True,(255,255,255)),(20,125))

    def draw(self):
        screen.fill((30,140,30))
        self.draw_road()

        for enemy in self.enemies:
            enemy.draw(screen)

        self.player.draw(screen)

        for p in self.particles[:]:
            p.update()
            p.draw(screen)
            if p.life <= 0:
                self.particles.remove(p)

        self.draw_weather()
        self.draw_hud()

    def run(self):
        running = True

        while running:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.state == "menu":
                    if event.type == pygame.KEYDOWN:
                        self.reset()

                elif self.state == "gameover":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        self.reset()

            if self.state == "menu":
                screen.fill((20,20,30))
                t1 = big_font.render("FACE RACER PRO",True,(255,255,255))
                t2 = font.render("Move your head to steer",True,(255,255,255))
                t3 = font.render("Press any key to start",True,(255,255,0))

                screen.blit(t1,(WIDTH//2-t1.get_width()//2,220))
                screen.blit(t2,(WIDTH//2-t2.get_width()//2,330))
                screen.blit(t3,(WIDTH//2-t3.get_width()//2,390))

            elif self.state == "playing":
                self.update_playing()
                self.draw()

            elif self.state == "gameover":
                self.draw()

                over = big_font.render("GAME OVER",True,(255,50,50))
                txt = font.render("Press R to Restart",True,(255,255,255))

                screen.blit(over,(WIDTH//2-over.get_width()//2,250))
                screen.blit(txt,(WIDTH//2-txt.get_width()//2,350))

            pygame.display.flip()

        self.face.close()
        cv2.destroyAllWindows()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()
