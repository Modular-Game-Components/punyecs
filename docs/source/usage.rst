Usage
=====

----------------------------
What is it? (And an Example)
----------------------------

Instead of requiring inheritance, one can specify which attributes to operate on and any object that has those attributes is then operated on. That is, if a ``Player`` has an ``x`` and ``y`` attribute and an (unrelated) ``Enemy`` class has an ``x`` and ``y`` attribute you can have them both influenced by a ``World`` object. This avoids complicated inheritance hierarchies.

Here is a small example to illustrate the above:

.. code-block:: python

   from dataclasses import dataclass
   from punyecs import World, requirements, Trait, give_traits
   
   w = World()
   Pos = Trait(x=0.0, y = 0.0)
   
   @dataclass
   @give_traits(Pos)
   class Player:
       pass

   @dataclass
   @give_traits(Pos)
   class Enemy:
       pass

   @requirements(w, Pos)
   def move(e, dt):
       e.x += 0.1
       e.y += 0.1

   player = Player(0.0, 0.0)
   enemy = Enemy(1.0, 1.0)
   w.add(player)
   w.add(enemy)

   w.update(1)
   print(player.x)
   # Prints 0.1
   print(player.y)
   # Prints 0.1

   print(enemy.x)
   # Prints 1.1
   print(enemy.y)
   # Prints 1.1

Be sure to read the comments! Observe the ``move`` function operates on *both* ``Player`` and ``Enemy`` even though they are unrelated.

.. note::

   We pass ``1`` to ``w.update(...)`` because in the video game context we virtually always want to pass some change in time *per frame* of the object. To keep the example simple, we disregard this value, however, you should consider passing ``dt`` in the game context. (For example, in Pygame, a game loop might look something like:

   .. code-block:: python

      ...
      dt = 0
      ...
      while True:
          w.update(dt)
          ...
          dt = clock.tick(60) / 1000

------------------------------
Fine Grained Control: Querying
------------------------------

Returning to the example above, we may want various enemies to move like above but instead want to allow controller input for the player object. We can avoid influencing the player object by putting it in the excluded objects list. The function ``move`` becomes:

.. code-block:: python

   @requirements(w, Pos, subject_to=c.isnot(player))
   def move(e, dt):
       e.x += 0.1
       e.y += 0.1

Then after every ``w.update(1)`` the ``player`` object *will still remain at* ``x=0.0``, ``y=0.0``.

----------------------------------------
An Alternative: Exclude Based on a Value
----------------------------------------

It could be that you have multiple characters that are controllable that are *not* the player. You could give them an attribute ``controller: bool = True``. Then exclude an object if it has the ``controller`` attribute *and* the ``controller`` attribute is ``True`` with the following ``subject_to`` constraint:

.. code-block:: python
   from punyecs import c

   @requirements(w, Pos, subject_to=c.controller.is_(True))
   def move(e, dt):
       e.x += 0.1
       e.y += 0.1

---------------------------------------------------
An Extension: Exclude Based on Attribute Predicates
---------------------------------------------------

Excluding based on the singular value of an attribute still might not be enough control. Suppose we have high level entities and low level entities and that most entities (except high level entities) are affected by gravity. More precisely, suppose high level enemies are those that have an attribute ``level > 50``. Gravity typically operates on the ``y`` attribute so we may write something like:

.. code-block:: python

   @requirements(w, YAxis, subject_to=c.level > 50)
   def gravity(e):
       e.y -= GRAVITY

-----------------------------
Excluding Based on Attributes
-----------------------------

We may not care what value the attribute is and simply want to exclude the object if it *has* that attribute. For instance, we may have many different kinds of creatures. Most can follow the usual movement update function, but some creatures have a ``wiggle`` attribute. ``wiggle`` could be a Boolean, or even something more sophisticated like a function that describes how the creature wiggles.

To illustrate this consider:

.. code-block:: python

   from dataclasses import dataclass
   from punyecs import World, requirements, Trait, give_traits, c, exattr

   w = World()
   Pos = Trait(x=0.0, y=0.0)

   @dataclass
   @give_traits(Pos)
   class Player:
       pass

   @dataclass
   @give_traits(Pos)
   class WalkingEnemy:
       pass

   @dataclass
   @give_traits(Pos)
   class Wiggler:
       wiggle: lambda x: x + 2

   @requirements(w, Pos, subject_to=exattr(c, "wiggle"))
   def move(e, dt):
       e.x += 0.1
       e.y += 0.1

   @requirements(w, Pos, subject_to=hasattr(c, "wiggle"))
   def wiggle(e, dt):
       e.x = wiggle(e.x)
       e.y = wiggle(e.y)


   player = Player(0.0, 0.0)
   enemy = Enemy(1.0, 1.0)
   wiggler = Wiggle(3.0, 3.0)
   w.add(player)
   w.add(enemy)
   w.add(wiggler)

   w.update(1)
   print(player.x)
   # Prints 0.1
   print(player.y)
   # Prints 0.1

   print(enemy.x)
   # Prints 1.1
   print(enemy.y)
   # Prints 1.1

   print(wiggler.x)
   # Prints 5.0
   print(wiggler.y)
   # Prints 5.0

-----------------------------------
Refinements on Updating: `one_shot`
-----------------------------------

`update` is often used in ECS, but what if you do not want to update every group? Furthermore, `update` is often in the gameloop, but what if you need to invoke a function on a bunch of objects outside the gameloop? This is where the
`one_shot` decorator comes into play.

Consider this simple setup:

.. code-block:: python

   from dataclasses import dataclass
   from punyecs import World, one_shot, Trait, give_traits, c

   Pos = Trait(x=0, y=0, z=0)

   @dataclass
   @give_traits(Pos, exclude={"x"})
   class Player:
       pass

   @dataclass
   @give_traits(Pos)
   class Enemy:
       pass

    @one_shot(w, Pos)
    def inc_x(e):
        e.x += 1

    e1 = Enemy(0, 0, 0)
    e2 = Enemy(0, 0, 0)
    p1 = Player(0, 0)

    w.add(e1)
    w.add(e2)
    w.add(p1)

What have we done? We've added one player and two enemies to a world `w`. Furthermore, we've added a `@one_shot` decorator. Thus, whenever we call `inc_x` *without arguments* it updates *every* enemy character (more precisely any object with `x`, `y`, and `z` attributes). Player remains the same because it lacks the `z` component. Thus, `inc_x()` can be placed anywhere and it will `update` a *specific* group of entities. So

.. code-block:: python

   >>> e1.x, e2.x, p1.x
   (0, 0, 0)
   >>> inc_x()
   >>> e1.x, e2.x, p1.x
   (1, 1, 0)
