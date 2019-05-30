import pygame
screen = pygame.display.set_mode((500, 500))
screen.fill((255,255,255))
timer = pygame.time.Clock()
ball = pygame.sprite.Sprite()
ball.image = pygame.image.load("throwball.png")
ball.image = pygame.transform.scale(ball.image, (48,48))
ball.rect = ball.image.get_rect(topleft = (50,50))
ball.orig_image = ball.image
rotaterect = pygame.Rect(ball.rect.left, ball.rect.top, ball.rect.width, ball.rect.height)

for i in range(60):
    pygame.draw.rect(screen, pygame.Color(255,255,255), ball.rect)
    ball.image = pygame.transform.rotate(ball.orig_image, i*20)
    ball.rect = ball.image.get_rect()
    ball.rect.center = (24 + 3*i, 24 + ((i-20)*(i-20) + 1)/6)
    screen.blit(ball.image, ball.rect)
    pygame.display.update()
    timer.tick(60)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
while 1:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()