Usage
=====

----------------------------
What is it? (And an Example)
----------------------------

Instead of requiring inheritance, one can specify which attributes to operate on and any objec that has those attributes is operated on. That is, if a ``Player`` has an ``x`` and ``y`` attribute and an (unrelated) ``Enemy`` class has an ``x`` and ``y`` attribute you can have them both influenced by a ``World`` object. This avoids complicated inheritance hierarchies.

Here is a small example to illustrate the above:

.. code-block:: python

   from dataclasses import dataclass
   from punyecs import World, requirements
   
   w = World()
   
   @dataclass
   class Player:
       x: float
       y: float

   @dataclass
   class Enemy:
       x: float
       y: float

   @requirements(w, {"x", "y"})
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

   We pass ``1`` to ``w.update(...)`` because in the video game context. We virtually always want to pass some change in time *per frame* of the object. To keep the example simple, we disregard this value, however, you should consider passing ``dt`` in the game context.

------------------------------
Fine Grained Control: Querying
------------------------------

Returning to the example above, we may want various enemies to move like above but instead want to allow controller input for the player object. We can avoid influencing the player object by putting it in the excluded objects list. The function ``move`` becomes:

.. code-block:: python

   @requirements(w, {"x", "y"}, exclude_objs=[player])
   def move(e, dt):
       e.x += 0.1
       e.y += 0.1

Then after every ``w.update(1)`` the ``player`` object *will still remain at* ``x=0.0``, ``y=0.0``.

-----------------------------
Excluding Based on Attributes
-----------------------------

It might be inconvenient to exclude individual objects if a large number of objects need to be excluded. ``punyecs`` provides a couple more filtering options. One way around this is to specify which attributes an object should *not* have.

For instance, we may have many different kinds of creatures. Most can follow the usual movement update function, but some creatures have a ``wiggle`` attribute. ``wiggle`` could be a Boolean, or even something more sophisticated like a function that describes how the creature wiggles.

To illustrate this consider:

.. code-block:: python

   from dataclasses import dataclass
   from punyecs import World, requirements

   w = World()

   @dataclass
   class Player:
       x: float
       y: float

   @dataclass
   class WalkingEnemy:
       x: float
       y: float

   @dataclass
   class Wiggler:
       x: float
       y: float
       wiggle: lambda x: x + 2

   @requirements(w, {"x", "y"}, exclude={"wiggle"})
   def move(e, dt):
       e.x += 0.1
       e.y += 0.1

   @requirements(w, {"wiggle", "x", "y"})
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
