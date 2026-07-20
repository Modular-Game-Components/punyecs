from dataclasses import dataclass
from punyecs import World, Query, query, requirements, one_shot, inject_attrs


def test_query():
    w = World()
    q = Query(and_attr={"x", "y"})

    @dataclass
    class Player:
        x: float
        y: float

    @dataclass
    class Enemy:
        x: float
        y: float

    @query(w, q)
    def f(e, dt):
        e.x += 0.1
        e.y += 0.1

    player = Player(0.0, 0.0)
    enemy = Enemy(0.0, 0.0)
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

def test_requirement():
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
    def f(e, dt):
        e.x += 0.1
        e.y += 0.1

    player = Player(0.0, 0.0)
    enemy = Enemy(0.0, 0.0)
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

def test_exclude_attr():
    w = World()

    @dataclass
    class Player:
        x: float
        y: float

    @dataclass
    class Enemy:
        x: float
        y: float

    player = Player(0.0, 0.0)
    enemy = Enemy(0.0, 0.0)

    q = Query(and_attr={"x", "y"}, exclude_objs=[player])

    @query(w, q)
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

def test_exclude_attr_val_query():
    w = World()

    @dataclass
    class Player:
        x: float
        y: float
        controller: bool = True

    @dataclass
    class Enemy:
        x: float
        y: float

    player = Player(0.0, 0.0)
    enemy = Enemy(0.0, 0.0)

    q = Query(and_attr={"x", "y"}, exclude_attr_vals={"controller": True})

    @query(w, q)
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

    @dataclass
    class Player:
        x: float
        y: float
        controller: bool = True

    @dataclass
    class Enemy:
        x: float
        y: float

    player = Player(0.0, 0.0)
    enemy = Enemy(0.0, 0.0)

    @requirements(w, {"x", "y"}, exclude_attr_vals={"controller": True})
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
    
    @dataclass
    class Player:
        x: int
        y: int

    @dataclass
    class Enemy:
        x: int
        y: int
        z: int

    @one_shot(w, {"x", "y", "z"})
    def inc_x(e):
        e.x += 1

    e1 = Enemy(0, 0, 0)
    e2 = Enemy(0, 0, 0)
    p1 = Player(0, 0)

    w.add(e1)
    w.add(e2)
    w.add(p1)

    assert(e1.x == 0)
    assert(e2.x == 0)
    assert(p1.x == 0)

    inc_x()

    assert(e1.x == 1)
    assert(e2.x == 1)
    assert(p1.x == 0)

    inc_x()

    assert(e1.x == 2)
    assert(e2.x == 2)
    assert(p1.x == 0)

def test_inject_attrs():
    coords = {"x": 0, "y": 0, "z": 0}

    @inject_attrs(coords, exclude={"z"})
    class Player:
        pass

    @inject_attrs(coords, override={"x": 1})
    class Enemy:
        pass

    @inject_attrs(coords)
    class Rock:
        pass

    player = Player()

    assert(player.x == 0)
    assert(player.y == 0)
    assert(not hasattr(player, "z"))

    enemy = Enemy()

    assert(enemy.x == 1)
    assert(enemy.y == 0)
    assert(enemy.z == 0)

    rock = Rock()

    assert(rock.x == 0)
    assert(rock.y == 0)
    assert(rock.z == 0)
