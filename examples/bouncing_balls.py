# pyrefly: ignore-errors

import random
import pygame
from punyecs import World, Trait, give_traits, requirements

WIDTH, HEIGHT = 640, 480
NUM_BALLS = 12

Physics = Trait(x=0.0, y=0.0, vx=0.0, vy=0.0)
Renderable = Trait(radius=8, color=(255, 255, 255))


@give_traits(Physics, Renderable)
class Ball:
    pass


def make_ball():
    ball = Ball()
    ball.x = random.uniform(0, WIDTH)
    ball.y = random.uniform(0, HEIGHT)
    ball.vx = random.uniform(-200, 200)
    ball.vy = random.uniform(-200, 200)
    ball.radius = random.randint(6, 16)
    ball.color = random.choice([(226, 90, 48), (55, 138, 221), (99, 153, 34)])
    return ball


world = World()

@requirements(world, Physics)
def move(entity, dt):
    entity.x += entity.vx * dt
    entity.y += entity.vy * dt
    if entity.x <= 0 or entity.x >= WIDTH:
        entity.vx = -entity.vx
    if entity.y <= 0 or entity.y >= HEIGHT:
        entity.vy = -entity.vy

ctx = {}

@requirements(world, Physics + Renderable)
def draw(entity, dt):
    pygame.draw.circle(
        ctx["surface"], entity.color, (int(entity.x), int(entity.y)), entity.radius
    )

balls = [make_ball() for _ in range(NUM_BALLS)]
world.extend(balls)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    ctx["surface"] = screen
    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((20, 20, 24))
        world.update(dt)  # runs move over its group, then draw over its
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
