from dataclasses import dataclass
from punyecs import World, Query, query, requirements


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

def test_exclude():
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

