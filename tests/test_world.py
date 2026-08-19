# pyrefly: ignore-errors

import dataclasses

from punyecs import Trait, World, c, give_traits, has_attr, one_shot, requirements


Pos = Trait(x=0.0, y=0.0)
Vel = Trait(vx=1.0, vy=2.0)
YAxis = Trait(y=0.0)
Stats = Trait(level=0)


def test_trait_combination():
    @give_traits(Pos + Vel)
    class Mover:
        pass

    m = Mover()
    assert m.x == 0.0
    assert m.y == 0.0
    assert m.vx == 1.0
    assert m.vy == 2.0


def test_multiple_traits():
    @give_traits(Pos, Vel)
    class Mover:
        pass

    m = Mover()
    assert m.x == 0.0
    assert m.vx == 1.0


def test_exclude_and_override_together():
    @give_traits(Pos, Vel, exclude={"y"}, override={"vx": 10.0})
    class Sprite:
        pass

    s = Sprite()
    assert s.x == 0.0
    assert not hasattr(s, "y")
    assert s.vx == 10.0
    assert s.vy == 2.0


def test_give_traits_makes_dataclass():
    @give_traits(Pos)
    class Thing:
        pass

    assert dataclasses.is_dataclass(Thing)


def test_update_respects_dt():
    w = World()

    @give_traits(Pos)
    class Player:
        pass

    @requirements(w, Pos)
    def move(e, dt):
        e.x += 0.5 * dt

    p = Player()
    w.add(p)
    w.update(2)
    assert p.x == 1.0


def test_systems_run_in_group_order():
    w = World()

    @give_traits(Pos)
    class Enemy:
        pass

    @requirements(w, Pos)
    def add_one(e, dt):
        e.x += 1

    @requirements(w, Pos)
    def double(e, dt):
        e.x *= 2

    e = Enemy()
    w.add(e)
    w.update(1)
    assert e.x == 2.0


def test_entity_added_after_system_declared():
    w = World()

    @give_traits(Pos)
    class Enemy:
        pass

    @requirements(w, Pos)
    def move(e, dt):
        e.x += 0.1

    e = Enemy()
    w.add(e)
    w.update(1)
    assert e.x == 0.1


def test_add_entity_after_first_update():
    w = World()

    @give_traits(Pos)
    class Enemy:
        pass

    @requirements(w, Pos)
    def move(e, dt):
        e.x += 1

    e1 = Enemy()
    w.add(e1)
    w.update(1)
    e2 = Enemy()
    w.add(e2)
    w.update(1)
    assert e1.x == 2
    assert e2.x == 1


def test_extend():
    w = World()

    @give_traits(Pos)
    class Enemy:
        pass

    @requirements(w, Pos)
    def move(e, dt):
        e.x += 1

    enemies = [Enemy() for _ in range(3)]
    w.extend(enemies)
    w.update(1)
    assert [e.x for e in enemies] == [1, 1, 1]


def test_remove_multiple():
    w = World()

    @give_traits(Pos)
    class Enemy:
        pass

    @one_shot(w, Pos)
    def inc_x(e):
        e.x += 1

    e1, e2, e3, e4 = Enemy(), Enemy(), Enemy(), Enemy()
    w.extend([e1, e2, e3, e4])
    inc_x()
    w.remove(e2, e4)
    inc_x()
    assert (e1.x, e2.x, e3.x, e4.x) == (2, 1, 2, 1)


def test_remove_unadded_entity_is_noop():
    w = World()

    @give_traits(Pos)
    class Enemy:
        pass

    @one_shot(w, Pos)
    def inc_x(e):
        e.x += 1

    e1 = Enemy()
    ghost = Enemy()
    w.add(e1)
    w.remove(ghost)
    inc_x()
    assert e1.x == 1


def test_subject_to_level_filter():
    w = World()

    @give_traits(YAxis, Stats, override={"level": 30})
    class Grunt:
        pass

    @give_traits(YAxis, Stats, override={"level": 80})
    class Elite:
        pass

    @requirements(w, YAxis, subject_to=c.level > 50)
    def gravity(e, dt):
        e.y -= 1.0 * dt

    grunt = Grunt()
    elite = Elite()
    w.add(grunt)
    w.add(elite)
    w.update(1)
    assert grunt.y == 0.0
    assert elite.y == -1.0


def test_isnot_exclusion():
    w = World()

    @give_traits(Pos)
    class Player:
        pass

    @give_traits(Pos)
    class Enemy:
        pass

    player = Player()
    enemy = Enemy()

    @requirements(w, Pos, subject_to=c.isnot(player))
    def move(e, dt):
        e.x += 0.1
        e.y += 0.1

    w.add(player)
    w.add(enemy)
    w.update(1)
    assert player.x == 0.0
    assert player.y == 0.0
    assert enemy.x == 0.1
    assert enemy.y == 0.1


def test_truthy_attribute_filter():
    w = World()

    @give_traits(Pos)
    class Player:
        controller: bool = True

    @give_traits(Pos)
    class Enemy:
        pass

    player = Player()
    enemy = Enemy()

    @requirements(w, Pos, subject_to=c.controller)
    def input(e, dt):
        e.x += 1

    w.add(player)
    w.add(enemy)
    w.update(1)
    assert player.x == 1.0
    assert enemy.x == 0.0


def test_has_attr_wiggle():
    w = World()

    @give_traits(Pos)
    class Plain:
        pass

    @give_traits(Pos)
    class Wiggler:
        wiggle = staticmethod(lambda x: x + 2)

    @requirements(w, Pos, subject_to=has_attr(c, "wiggle"))
    def wiggle(e, dt):
        e.x = e.wiggle(e.x) * dt

    plain = Plain()
    wiggler = Wiggler()
    w.add(plain)
    w.add(wiggler)
    w.update(1)
    assert plain.x == 0.0
    assert wiggler.x == 2.0


def test_one_shot_with_subject_to():
    w = World()

    @give_traits(Pos)
    class Enemy:
        pass

    e1 = Enemy()
    e1.level = 10
    e2 = Enemy()
    e2.level = 100

    @one_shot(w, Pos, subject_to=c.level > 50)
    def reward(e):
        e.x += 10

    w.add(e1)
    w.add(e2)
    reward()
    assert e1.x == 0.0
    assert e2.x == 10.0


def test_requirements_wraps_function():
    w = World()

    @give_traits(Pos)
    class Enemy:
        pass

    @requirements(w, Pos)
    def move(e, dt):
        e.x += dt
        return e.x

    e = Enemy()
    w.add(e)
    result = move(e, 2)
    assert result == 2.0


def test_add_without_groups():
    w = World()

    @give_traits(Pos)
    class Enemy:
        pass

    e = Enemy()
    w.add(e)
    assert e in w.entities
    assert w.groups == []