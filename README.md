<p align="center">
  <img src="punyecs-logo.svg" alt="punyecs">
</p>

# punyecs

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Modular-Game-Components/punyecs/pytest.yml)

`punyecs` is a tiny Entity Component System (ECS) inspired by [tiny-ecs](https://github.com/bakpakin/tiny-ecs) for Python. `punyecs` operates directly on class attributes as opposed to creating components along with querying mechanisms for fine grain control over which objects are operated on by systems similar to how tiny-ecs works on Lua tables. Decouple what an object can do from what it inherits.

# Quick Install

If you use [pip](https://pypi.org/project/pip/):

```
pip install punyecs
```

If you use [uv](https://github.com/astral-sh/uv):

```
uv add punyecs
```

# What is it?

Instead of requiring inheritance, one can specify which attributes to operate on and any object (regardless of class) that has those attributes is operated on. That is, if a `Player` has an `x` and `y` attribute and an (unrelated) `Enemy` class has an `x` and `y` attribute you can have them both influenced by a `World` object. This avoids complicated inheritance hierarchies.

Here is a small example to illustrate the above:

```py
from punyecs import World, requirements, Trait, give_traits

w = World()
Pos = Trait(x=0.0, y=0.0)

@give_traits(Pos)
class Player:
    pass

@give_traits(Pos, override={"x": 1.0, "y": 1.0})
class Enemy:
    pass

@requirements(w, Pos)
def move(e, dt):
    e.x += 0.1
    e.y += 0.1

player = Player()
enemy = Enemy()
w.add(player)
w.add(enemy)

w.update(1)
print(player.x) # Prints 0.1
print(player.y) # Prints 0.1

print(enemy.x) # Prints 1.1
print(enemy.y) # Prints 1.1
```

# A Bit More Sophistication

We may also do exclusions for fine grain control. Returning to the example above, we may want various enemies to move like above but instead want to allow controller input for the `player` object. We can avoid influencing the `player` object by putting it in the excluded objects list. The function `f` becomes:

```py
from punyecs import c

# ...

@requirements(w, Pos, subject_to=c.isnot(player))
def move(e, dt):
    e.x += 0.1
    e.y += 0.1
```

Then after every `world.update(1)`, the `player` object *will still remain at* `x=0.0`, `y=0.0`.

# Even More Sophistication!

It might be inconvenient to exclude *individual* objects if a large number of objects need to be excluded. `punyecs` provides a couple more filtering options. One way around this is to specify which attributes an object should *not* have.

For instance, we may have many different kinds of creatures. Most can follow the usual movement update function, but some creatures have a `wiggle` attribute. `wiggle` could be a Boolean, or even something more sophisticated like a function that describes how the creature wiggles.

To illustrate this consider:

```py
from punyecs import World, requirements, Trait, give_traits, c, exattr

w = World()
Pos = Trait(x=0.0, y=0.0)

@give_traits(Pos)
class Player:
    pass

@give_traits(Pos, override={"x": 1.0, "y": 1.0})
class Enemy:
    pass

@give_traits(Pos, override={"x": 3.0, "y": 3.0})
class Wiggler:
    wiggle = lambda x: x + 2

@requirements(w, Pos, subject_to=exattr(c, "wiggle"))
def move(e, dt):
    e.x += 0.1
    e.y += 0.1

@requirements(w, Pos, subject_to=hasattr(c, "wiggle"))
def wiggle(e, dt):
    e.x = wiggle(e.x)
    e.y = wiggle(e.y)


player = Player()
enemy = Enemy()
wiggler = Wiggle()
w.add(player)
w.add(enemy)
w.add(wiggler)

w.update(1)
print(player.x) # Prints 0.1
print(player.y) # Prints 0.1

print(enemy.x) # Prints 1.1
print(enemy.y) # Prints 1.1

print(wiggler.x) # Prints 5.0
print(wiggler.y) # Prints 5.0
```

Thus, `move` does not operate on `wiggler` but `wiggle` does.

# How does punyecs compare to Esper?

[Esper](https://github.com/benmoran56/esper) is a well-established, performance-focused ECS for Python, and a reasonable default choice for most games. punyecs takes a different set of trade-offs — here's how they differ in practice.

## Entities: opaque IDs vs. your own objects

In Esper, an entity is just an integer ID. Components are separate classes you attach to that ID, and you get data back as tuples when you query:

```python
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
```

In punyecs, the entity *is* your own object — a `Player` instance, not an ID you look up. Traits attach real attributes directly to that object:

```python
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
```

If your game logic elsewhere already wants to hold a reference to "the player" and call methods on it, poke at `player.x` directly, pass it to non-ECS code, etc., punyecs avoids the ID indirection. If you'd rather never think about a "player object" at all and treat everything as anonymous component tuples, Esper's model is more purely data-oriented.

## Systems: classes vs. plain functions

Esper systems are `Processor` subclasses with a `process()` method, added to the `World` and run in priority order. punyecs systems are plain functions decorated with `@requirements` (or `@one_shot` for on-demand, outside-the-game-loop calls) — there's no class boilerplate, but you also don't get Esper's `Processor` priority system out of the box.

## Filtering entities

This is where punyecs' newer `subject_to` query DSL earns its keep. In Esper, once `get_components` gives you a matching set, any further filtering (skip the player, skip anything below a level threshold) is a plain `if` you write yourself inside `process()`. In punyecs, that filtering is declared right in the decorator:

```python
@requirements(w, Pos, subject_to=c.level > 50)
def gravity(e, dt):
    e.y -= GRAVITY * dt
```

That's a real ergonomic win for filters you reuse often, at the cost of one more concept (the `c` proxy) to learn.

## Performance

Esper is explicitly built for performance: entities as bare integers, cached query results, and a design lineage aimed at large entity counts. punyecs hasn't been benchmarked against it, and the attribute-matching/structural-typing approach it uses is unlikely to out-perform Esper's tuple-of-components model at scale — if raw throughput on thousands of entities is your top priority, Esper is the safer bet today. punyecs' focus instead is ergonomics: fewer moving parts for small-to-medium games, and letting entities stay as ordinary Python objects instead of IDs.

## When to reach for which

- **Esper** — you want a mature, widely-used, performance-oriented ECS, and you're comfortable with the classic "entities are IDs, components are separate objects" model.
- **punyecs** — you want your entities to stay as normal Python objects (dataclasses you can pass around, inspect, and extend), you like declaring filters inline via `subject_to`, and you're building something small-to-medium where Esper's performance headroom isn't the deciding factor.

# Documentation

Even more filtering options are available. To learn more, see the [readthedocs.](https://punyecs.readthedocs.io/en/latest/index.html)

# Contributing

Feel free to [file an issue](https://github.com/Modular-Game-Components/punyecs/issues), [make a pull request](https://github.com/Modular-Game-Components/punyecs/pulls) or, if you really like the project, [donate.](https://www.paypal.com/donate/?business=9ZQ9S6RJBVATY&no_recurring=0&currency_code=USD) (No pressure though.)
