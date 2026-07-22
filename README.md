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
from dataclasses import dataclass
from punyecs import World, requirements, Trait, give_traits

w = World()
Pos = Trait(x=0.0, y=0.0)

@dataclass
@give_traits(Pos)
class Player:
    pass

@dataclass
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
class Enemy:
    pass

@dataclass
@give_traits(Pos)
class Wiggler:
    wiggle = lambda x: x + 2

@requirements(w, Pos, subject_to=exattr(c, "wiggle"))
def move(e, dt):
    e.x += 0.1
    e.y += 0.1

@requirements(w, Pos + Trait(wiggle=None))
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
print(player.x) # Prints 0.1
print(player.y) # Prints 0.1

print(enemy.x) # Prints 1.1
print(enemy.y) # Prints 1.1

print(wiggler.x) # Prints 5.0
print(wiggler.y) # Prints 5.0
```

Thus, `move` does not operate on `wiggler` but `wiggle` does.

# Documentation

Even more filtering options are available. To learn more, see the [readthedocs.](https://punyecs.readthedocs.io/en/latest/index.html)

# Contributing

Feel free to [file an issue](https://github.com/Modular-Game-Components/punyecs/issues), [make a pull request](https://github.com/Modular-Game-Components/punyecs/pulls) or, if you really like the project, [donate.](https://www.paypal.com/donate/?business=9ZQ9S6RJBVATY&no_recurring=0&currency_code=USD) (No pressure though.)
