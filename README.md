<p align="center">
  <img src="punyecs-logo.svg" alt="punyecs">
</p>

# punyecs

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/Modular-Game-Components/punyecs/pytest.yml)
![PyPI Python Version](https://img.shields.io/pypi/pyversions/punyecs)

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

We may also do exclusions for fine grain control. Returning to the example above, we may want various enemies to move like above but instead want to allow controller input for the `player` object. We can avoid influencing the `player` object by using a querying DSL. The function `move` becomes:

```py
from punyecs import c

# ...

@requirements(w, Pos, subject_to=c.isnot(player))
def move(e, dt):
    e.x += 0.1
    e.y += 0.1
```

Then after every `world.update(1)`, the `player` object *will still remain at* `x=0.0`, `y=0.0`.

# A Graphical Pygame Example

https://github.com/user-attachments/assets/682ea45e-18a1-4d3e-9176-59686a80a524

Check out the `examples` folder!

# How does punyecs compare to Esper?

[Esper](https://github.com/benmoran56/esper) is a well-established, performance-focused ECS for Python, and a reasonable default choice for most games. punyecs takes a different set of trade-offs — here's how they differ in practice:

- **Esper** — you want a mature, widely-used, performance-oriented ECS, and you're comfortable with the classic "entities are IDs, components are separate objects" model.
- **punyecs** — you want your entities to stay as normal Python objects (dataclasses you can pass around, inspect, and extend), you like declaring filters inline via `subject_to`, and you're building something small-to-medium where Esper's performance headroom isn't the deciding factor.

For a more detailed comparison see [this section](https://punyecs.readthedocs.io/en/latest/esper.html) of the documentation.

# Documentation

Even more filtering options are available. To learn more, see the [readthedocs.](https://punyecs.readthedocs.io/en/latest/index.html)

# Contributing

Feel free to [file an issue](https://github.com/Modular-Game-Components/punyecs/issues), [make a pull request](https://github.com/Modular-Game-Components/punyecs/pulls) or, if you really like the project, [donate.](https://www.paypal.com/donate/?business=9ZQ9S6RJBVATY&no_recurring=0&currency_code=USD) (No pressure though.)
