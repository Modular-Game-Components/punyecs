=======================
A Simple Pygame Example
=======================

We will be building a small `Pygame <https://pyga.me/docs/>`_ application that has some balls bouncing around the screen. A video of it can be found `here <https://github.com/Modular-Game-Components/punyecs#a-graphical-pygame-example>`_.

------------------------------
The Fundamental Pygame Example
------------------------------

First, we recomend you familiarize your self with the basic `Pygame example <https://pyga.me/docs/>`_:

.. code-block:: python

   # Example file showing a basic pygame "game loop"
   import pygame

   # pygame setup
   pygame.init()
   screen = pygame.display.set_mode((1280, 720))
   clock = pygame.time.Clock()
   running = True

   while running:
       # poll for events
       # pygame.QUIT event means the user clicked X to close your window
       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               running = False

       # fill the screen with a color to wipe away anything from last frame
       screen.fill("purple")

       # RENDER YOUR GAME HERE

       # flip() the display to put your work on screen
       pygame.display.flip()

       clock.tick(60)  # limits FPS to 60

   pygame.quit()

-----------------
Some Small Tweaks
-----------------

Once you have familiarized yourself with the example above, we are going to make a couple small changes to better organize the code:

.. code-block:: python

   import random
   import pygame
   from punyecs import World, Trait, give_traits, requirements


   WIDTH, HEIGHT = 640, 480

   ctx = {}

   def main():
       # pygame setup
       pygame.init()
       screen = pygame.display.set_mode((1280, 720))
       ctx["surface"] = screen
       clock = pygame.time.Clock()
       running = True

       while running:
           dt = clock.tick(60) / 1000
           for event in pygame.event.get():
               if event.type == pygame.QUIT:
                   running = False

           screen.fill((20, 20, 24))
           pygame.display.flip()


       pygame.quit()
   
   if __name__ == '__main__':
       main()

Here's a brief summary of what we did (it was mostly just for better organization):

* Put everything in a ``main`` function (good practice).
* Store the clock tick times in ``dt = clock.tick(60) / 1000`` (needed for ``punyecs``).
* Stored ``screen`` surface in a global variable ``ctx`` (short for "context") which we will use later outside of main.
* Misc. small tweaks: ``WIDTH``, ``HEIGHT`` constants, slight change of background color, ``punyecs`` imports, etc.

-----------
Some Traits
-----------

The balls bouncing around the screen have two properties (a.k.a. ``Traits``):

* They are affected by physics.
  * That is, they have a position and a velocity.
* They can be rendered to the screen.
  * That is, they have a radius and color.

Thus, we create the following traits:

.. code-block:: python

   # Note: We will override these values later.
   Physics = Trait(x=0.0, y=0.0, vx=0.0, vy=0.0)
   Renderable = Trait(radius=8, color=(255, 255, 255))

And, we must create a ``Ball`` class with these traits.

.. code-block:: python

   @give_traits(Physics, Renderable)
   class Ball:
       pass

And we will make a function that creates balls (and overrides the trait values):

.. code-block:: python
 
   def make_ball():
       ball = Ball()
       ball.x = random.uniform(0, WIDTH)
       ball.y = random.uniform(0, HEIGHT)
       ball.vx = random.uniform(-200, 200)
       ball.vy = random.uniform(-200, 200)
       ball.radius = random.randint(6, 16)
       ball.color = random.choice([(226, 90, 48), (55, 138, 221), (99, 153, 34)])
       return ball

---------
The World
---------

Now we make a ``World`` object and define the systems it runs on specified traits.

.. code-block:: python

   world = World()

To add the entities to the world:

.. code-block:: python

   NUM_BALLS = 12
   balls = [make_ball() for _ in range(NUM_BALLS)]
   world.extend(balls)

Great! Now all that remains is defining how the world interacts with the balls. We define a ``move`` function that operates on all things with a ``Physics`` trait:

.. code-block:: python

   @requirements(world, Physics)
   def move(entity, dt):
       entity.x += entity.vx * dt
       entity.y += entity.vy * dt
       if entity.x <= 0 or entity.x >= WIDTH:
           entity.vx = -entity.vx
       if entity.y <= 0 or entity.y >= HEIGHT:
           entity.vy = -entity.vy

That is, move a ball (or any physical thing!) and if it hits a wall, negate the direction to make it "bounce off" the wall.

Next, we have to draw, this will operate on objects with a ``Physics`` trait (for ``x`` and ``y`` in particular) and ``Renderable`` traits:

.. code-block:: python

   @requirements(world, Physics + Renderable)
   def draw(entity, dt):
       pygame.draw.circle(
           ctx["surface"], entity.color, (int(entity.x), int(entity.y)), entity.radius
       )

See? We used the global ``ctx`` to extract the surface and then we simply draw a circle where the entity should be (from the ``Physics`` trait) with the corresponding radius and color (from the ``Renderable`` trait).

Lastly, we must update the world in the game loop with ``world.update(dt)``. All in all we get:

.. code-block:: python

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
