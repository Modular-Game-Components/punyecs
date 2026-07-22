==================================
How does punyecs compare to Esper?
==================================

`Esper <https://github.com/benmoran56/esper>`_ is a well-established, performance-focused ECS for Python, and a reasonable default choice for most games. punyecs takes a different set of trade-offs — here's how they differ in practice.

-----------------------------------------
Entities: opaque IDs vs. your own objects
-----------------------------------------

In Esper, an entity is just an integer ID. Components are separate classes you attach to that ID, and you get data back as tuples when you query:

.. code-block:: python

   import esper
   from dataclasses import dataclass as component

   @component
   class Position:
       x: float = 0.0
       y: float = 0.0

   @component
   class Velocity:
       x: float = 0.0
       y: float = 0.0

   world = esper.World()
   player = world.create_entity(Position(0.0, 0.0), Velocity(2.0, 2.0))

   class MovementProcessor(esper.Processor):
       def process(self, dt):
           for ent, (pos, vel) in self.world.get_components(Position, Velocity):
               pos.x += vel.x * dt
               pos.y += vel.y * dt

In punyecs, the entity *is* your own object — a ``Player`` instance, not an ID you look up. Traits attach real attributes directly to that object:

.. code-block:: python

   from dataclasses import dataclass
   from punyecs import World, requirements, Trait, give_traits

   w = World()
   Pos = Trait(x=0.0, y=0.0)
   Vel = Trait(vx=0.0, vy=0.0)

   @dataclass
   @give_traits(Pos, Vel)
   class Player:
       pass

   @requirements(w, Pos)
   def move(e, dt):
       e.x += e.vx * dt
       e.y += e.vy * dt

   player = Player(0.0, 0.0)
   w.add(player)

If your game logic elsewhere already wants to hold a reference to "the player" and call methods on it, poke at ``player.x`` directly, pass it to non-ECS code, etc., punyecs avoids the ID indirection. If you'd rather never think about a "player object" at all and treat everything as anonymous component tuples, Esper's model is more purely data-oriented.

------------------------------------
Systems: classes vs. plain functions
------------------------------------

Esper systems are ``Processor`` subclasses with a ``process()`` method, added to the ``World`` and run in priority order. punyecs systems are plain functions decorated with ``@requirements`` (or ``@one_shot`` for on-demand, outside-the-game-loop calls) — there's no class boilerplate, but you also don't get Esper's ``Processor`` priority system out of the box.

------------------
Filtering entities
------------------

This is where punyecs' newer ``subject_to`` query DSL earns its keep. In Esper, once ``get_components`` gives you a matching set, any further filtering (skip the player, skip anything below a level threshold) is a plain ``if`` you write yourself inside ``process()``. In punyecs, that filtering is declared right in the decorator:

.. code-block:: python

   @requirements(w, Pos, subject_to=c.level > 50)
   def gravity(e):
       e.y -= GRAVITY

That's a real ergonomic win for filters you reuse often, at the cost of one more concept (the ``c`` proxy) to learn.

-----------
Performance
-----------

Esper is explicitly built for performance: entities as bare integers, cached query results, and a design lineage aimed at large entity counts. punyecs hasn't been benchmarked against it, and the attribute-matching/structural-typing approach it uses is unlikely to out-perform Esper's tuple-of-components model at scale — if raw throughput on thousands of entities is your top priority, Esper is the safer bet today. punyecs' focus instead is ergonomics: fewer moving parts for small-to-medium games, and letting entities stay as ordinary Python objects instead of IDs.

-----------------------
When to reach for which
-----------------------

- **Esper** — you want a mature, widely-used, performance-oriented ECS, and you're comfortable with the classic "entities are IDs, components are separate objects" model.
- **punyecs** — you want your entities to stay as normal Python objects (dataclasses you can pass around, inspect, and extend), you like declaring filters inline via ``subject_to``, and you're building something small-to-medium where Esper's performance headroom isn't the deciding factor.
