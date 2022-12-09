import pygame
from dataclasses import dataclass
from random import randint

pygame.init()

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

dis = pygame.display.set_mode((400, 600))
pygame.display.set_caption('Змейка от Skillbox')

game_over = False
x1 = 200
x1_change = 0
clock = pygame.time.Clock()


@dataclass
class Block:
    x: int
    y: int
    speed: int


blocks = []

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                x1_change = -10
            elif event.key == pygame.K_RIGHT:
                x1_change = 10
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                x1_change = 0
            elif event.key == pygame.K_RIGHT:
                x1_change = 0
    x1 += x1_change
    dis.fill(white)

    pygame.draw.rect(dis, black, [x1, 580, 120, 30])
    for block in blocks:
        pygame.draw.rect(dis, red, [block.x, block.y, 50, 50])
        
        block.y += block.speed
        block.speed *= 1.04
        
        if block.y > 600:
            blocks.remove(block)
        
        if block.y + 50 >= 580:
            if block.x > x1 and block.x < x1+120:
                game_over = True
            elif block.x+50 > x1 and block.x+50 < x1+120:
                game_over = True
        
    if len(blocks) == 0:
        blocks.append(Block(randint(0, 400-50), 0-50, 5))
        blocks.append(Block(randint(0, 400-50), 0-50, 5))

    pygame.display.update()
    clock.tick(30)

pygame.quit()
quit()
