from dataclasses import dataclass
from punyecs import World, Trait, requirements, one_shot, give_traits, exattr, c


def test_query():
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

    @requirements(w, Pos)
    def f(e, dt):
        e.x += 0.1
        e.y += 0.1

    player = Player()
    enemy = Enemy()
    w.add(player)
    w.add(enemy)

    assert player.x == 0.0
    assert player.y == 0.0
    assert enemy.x == 0.0
    assert enemy.y == 0.0


    w.update(1)
    assert player.x == 0.1
    assert player.y == 0.1
    assert enemy.x == 0.1
    assert enemy.y == 0.1

    w.update(1)
    assert player.x == 0.2
    assert player.y == 0.2
    assert enemy.x == 0.2
    assert enemy.y == 0.2

def test_requirement():
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

    @requirements(w, Pos)
    def f(e, dt):
        e.x += 0.1
        e.y += 0.1

    player = Player()
    enemy = Enemy()
    w.add(player)
    w.add(enemy)

    assert player.x == 0
    assert player.y == 0
    assert enemy.x == 0
    assert enemy.y == 0


    w.update(1)
    assert player.x == 0.1
    assert player.y == 0.1
    assert enemy.x == 0.1
    assert enemy.y == 0.1

    w.update(1)
    assert player.x == 0.2
    assert player.y == 0.2
    assert enemy.x == 0.2
    assert enemy.y == 0.2

def test_exclude_attr_val_query():
    w = World()
    Pos = Trait(x=0.0, y=0.0)

    @dataclass
    @give_traits(Pos)
    class Player:
        controller: bool = True

    @dataclass
    @give_traits(Pos)
    class Enemy:
        pass

    player = Player()
    enemy = Enemy()

    @requirements(w, Pos, subject_to=exattr(c, "controller"))
    def f(e, dt):
        e.x += 0.1
        e.y += 0.1

    w.add(player)
    w.add(enemy)

    assert player.x == 0.0
    assert player.y == 0.0
    assert enemy.x == 0.0
    assert enemy.y == 0.0


    w.update(1)
    assert player.x == 0.0
    assert player.y == 0.0
    assert enemy.x == 0.1
    assert enemy.y == 0.1

    w.update(1)
    assert player.x == 0.0
    assert player.y == 0.0
    assert enemy.x == 0.2
    assert enemy.y == 0.2

def test_exclude_attr_val_req():
    w = World()
    Pos = Trait(x=0.0, y=0.0)

    @dataclass
    @give_traits(Pos)
    class Player:
        controller: bool = True

    @dataclass
    @give_traits(Pos)
    class Enemy:
        pass

    player = Player()
    enemy = Enemy()

    @requirements(w, Pos, subject_to=exattr(c, "controller"))
    def f(e, dt):
        e.x += 0.1
        e.y += 0.1

    w.add(player)
    w.add(enemy)

    assert player.x == 0.0
    assert player.y == 0.0
    assert enemy.x == 0.0
    assert enemy.y == 0.0


    w.update(1)
    assert player.x == 0.0
    assert player.y == 0.0
    assert enemy.x == 0.1
    assert enemy.y == 0.1

    w.update(1)
    assert player.x == 0.0
    assert player.y == 0.0
    assert enemy.x == 0.2
    assert enemy.y == 0.2


def test_one_shot():
    w = World()
    Pos = Trait(x=0.0, y=0.0, z=0.0)
    
    @dataclass
    @give_traits(Pos, exclude={"z"})
    class Player:
        pass

    @dataclass
    @give_traits(Pos)
    class Enemy:
        pass

    @one_shot(w, Pos)
    def inc_x(e):
        e.x += 1

    e1 = Enemy()
    e2 = Enemy()
    p1 = Player()

    w.add(e1)
    w.add(e2)
    w.add(p1)

    assert(e1.x == 0.0)
    assert(e2.x == 0.0)
    assert(p1.x == 0.0)

    inc_x()

    assert(e1.x == 1.0)
    assert(e2.x == 1.0)
    assert(p1.x == 0.0)

    inc_x()

    assert(e1.x == 2.0)
    assert(e2.x == 2.0)
    assert(p1.x == 0.0)

def test_inject_attrs():
    Pos = Trait(x=0, y=0, z=0)

    @dataclass
    @give_traits(Pos, exclude={"z"})
    class Player:
        pass

    @dataclass
    @give_traits(Pos, override={"x": 1})
    class Enemy:
        pass

    @dataclass
    @give_traits(Pos)
    class Rock:
        pass

    player = Player()

    # pyrefly: ignore[missing-attribute] 
    assert(player.x == 0)
    # pyrefly: ignore[missing-attribute] 
    assert(player.y == 0)
    assert(not hasattr(player, "z"))

    enemy = Enemy()

    # pyrefly: ignore[missing-attribute] 
    assert(enemy.x == 1)
    # pyrefly: ignore[missing-attribute] 
    assert(enemy.y == 0)
    # pyrefly: ignore[missing-attribute] 
    assert(enemy.z == 0)

    rock = Rock()

    # pyrefly: ignore[missing-attribute] 
    assert(rock.x == 0)
    # pyrefly: ignore[missing-attribute] 
    assert(rock.y == 0)
    # pyrefly: ignore[missing-attribute] 
    assert(rock.z == 0)
