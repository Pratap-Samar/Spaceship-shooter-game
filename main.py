import pygame
import random
from os.path import join

from pygame.sprite import Group
import pygame.sprite

class Player(pygame.sprite.Sprite):
    def __init__(self,groups):
        super().__init__(groups)
        self.image =  pygame.image.load(join('assets/images/player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH /2, WINDOW_HEIGHT/2))
        self.direction = pygame.Vector2()
        self.speed = 300

        #laser cooldown
        self.can_shoot = True
        self.laser_time = 0
        self.cooldown = 250

        #Mask for pixel-perfect collision
        self.mask = pygame.mask.from_surface(self.image)

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.cooldown:
                self.can_shoot = True

    def update(self,dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN] - int(keys[pygame.K_UP]))
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))  # From Laser class
            self.can_shoot = False
            self.laser_time = pygame.time.get_ticks()
        self.laser_timer()
            
class Star(pygame.sprite.Sprite):
    def __init__(self,groups,surf):
        super().__init__(groups)
        self.image = surf
        self.rect =  self.image.get_frect(center = (random.randint(0, WINDOW_WIDTH),random.randint(0,WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
    
    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill   #To kill sprites when it leaves visible widnow

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 2000
        self.direction = pygame.Vector2(random.uniform( -0.5,0.5),1)
        self.speed = random.randint(100,200)
        #mask for pixel perfect collison
        self.mask = pygame.mask.from_surface(self.image)
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill

#=============== COLLISION FUNCTION =============
def collisions():
    global game_state,score

    # Player-Meteor Collision
    for meteor in meteor_sprites:
        if pygame.sprite.collide_mask(player, meteor):
           game_state = "game_over"

    # Laser-Meteor Collision
    for laser in laser_sprites:
        if pygame.sprite.spritecollide(laser, meteor_sprites,True):
            laser.kill()
            score += 1

#================= GAME OVER SCREEN ================
def game_over():
    global font,score
    # display game over and score
    display_surface.fill("red")
    game_over_surf = font.render(f"Game Over! Your score is {score}", True, "black")
    game_over_rect = game_over_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    display_surface.blit(game_over_surf, game_over_rect)   
    
    # Display instructions to restart or quit
    instruction_surf = font.render("Press R to Restart or Q to Quit", True, "white")
    instruction_rect = instruction_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 100))
    display_surface.blit(instruction_surf, instruction_rect)

    pygame.display.update()


#============ INITIALIZATING PYGAME MODULE ===========
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720
display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
pygame.display.set_caption("Spaceship Shooter")
running = True
clock = pygame.time.Clock()
score = 0
game_state = "playing"

#============ IMPORTING SPRITES AND SURFACE===========
#Sprites
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
player = Player(all_sprites)

#Surfaces
laser_surf = pygame.image.load(join('assets','images','laser.png')).convert_alpha()
meteor_surf = pygame.image.load(join('assets','images','meteor.png')).convert_alpha()
star_surf = pygame.image.load(join('assets','images','star.png')).convert_alpha()
font = pygame.font.Font(join('assets','font','Oxanium-Bold.ttf'), 40)

# for generating stars at random positions
for i in range(40):
    Star(all_sprites,star_surf)

#============ CREATING CUSTOM EVENT FOR METEOR===========
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event,600)

#======================= EVENT LOOP ======================
while running:
    dt = clock.tick() / 600

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == "playing":
            if event.type == meteor_event:
                x, y = random.randint(0, WINDOW_WIDTH), random.randint(-100, 0)
                Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))
        if game_state == "game_over" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Restart
                game_state = "playing"
                score = 0
                all_sprites.empty()
                meteor_sprites.empty()
                laser_sprites.empty()
                player = Player(all_sprites)
                for i in range(40):
                    Star(all_sprites, star_surf)
            elif event.key == pygame.K_q:  # Quit
                running = False

#================ DRAWING THE GAME ===============
    if game_state == "playing":
        all_sprites.update(dt)
        collisions()
        display_surface.fill("black")
        all_sprites.draw(display_surface)
        Score_surf = font.render(f'Score:{score}', True, 'white')
        Score_rect = Score_surf.get_frect(midtop = (WINDOW_WIDTH/2, 10))
        display_surface.blit(Score_surf, Score_rect)
        pygame.display.update()
    elif game_state == "game_over":
        game_over()
    
    pygame.display.update()

pygame.quit()
