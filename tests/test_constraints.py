# pyrefly: ignore-errors

from punyecs import (
    Query,
    Trait,
    and_,
    c,
    entity_satisfies_query,
    ex_attr,
    give_traits,
    has_attr,
    not_,
    or_,
)


@give_traits(Trait(x=1.0, y=2.0, level=10, count=5, name="orc"))
class DummyEntity:
    pass


def make_entity():
    return DummyEntity()


def test_attribute_access():
    e = make_entity()
    c._obj = e
    assert c.x.eval() == 1.0
    assert c.level.eval() == 10
    c._obj = None


def test_missing_attribute_evaluates_false():
    e = make_entity()
    c._obj = e
    assert c.missing.eval() is False
    c._obj = None


def test_arithmetic_operators():
    e = make_entity()
    c._obj = e
    assert (c.x + 1).eval() == 2.0
    assert (c.x - 1).eval() == 0.0
    assert (c.x * 2).eval() == 2.0
    assert (c.x / 2).eval() == 0.5
    assert (c.count // 2).eval() == 2
    c._obj = None


def test_reflected_arithmetic_operators():
    e = make_entity()
    c._obj = e
    assert (1 + c.x).eval() == 2.0
    assert (2 * c.x).eval() == 2.0
    assert (1 - c.x).eval() == 0.0
    assert (2 / c.x).eval() == 2.0
    assert (10 // c.count).eval() == 2
    c._obj = None


def test_unary_operators():
    e = make_entity()
    c._obj = e
    assert (-c.x).eval() == -1.0
    assert (abs(c.x - 10)).eval() == 9.0
    assert (~c.count).eval() == -6
    c._obj = None


def test_comparison_operators():
    e = make_entity()
    c._obj = e
    assert (c.level > 5).eval() is True
    assert (c.level < 5).eval() is False
    assert (c.level == 10).eval() is True
    assert (c.name == "orc").eval() is True
    c._obj = None


def test_is_and_isnot():
    e = make_entity()
    other = make_entity()
    c._obj = e
    assert c.is_(e).eval() is True
    assert c.is_(other).eval() is False
    assert c.isnot(e).eval() is False
    assert c.isnot(other).eval() is True
    c._obj = None


def test_not_():
    e = make_entity()
    c._obj = e
    assert not_(c.level > 5).eval() is False
    assert not_(c.level > 100).eval() is True
    c._obj = None


def test_bitwise_and_or_operators():
    e = make_entity()
    c._obj = e
    assert ((c.level > 5) & (c.count > 3)).eval() is True
    assert ((c.level > 5) & (c.count > 100)).eval() is False
    assert ((c.level > 100) | (c.count > 3)).eval() is True
    assert ((c.level > 100) | (c.count > 100)).eval() is False
    c._obj = None


def test_nested_arithmetic():
    e = make_entity()
    c._obj = e
    assert ((c.x + c.y) * 2).eval() == 6.0
    assert ((c.x + c.y) / 3).eval() == 1.0
    assert ((c.x + 2) * 2 > 5).eval() is True
    c._obj = None


def test_has_attr_and_ex_attr():
    e = make_entity()
    assert entity_satisfies_query(e, Query(Trait(), has_attr(c, "level"))) is True
    assert entity_satisfies_query(e, Query(Trait(), has_attr(c, "missing"))) is False
    assert entity_satisfies_query(e, Query(Trait(), ex_attr(c, "level"))) is False
    assert entity_satisfies_query(e, Query(Trait(), ex_attr(c, "missing"))) is True


def test_entity_satisfies_query_attributes():
    e = make_entity()
    assert entity_satisfies_query(e, Query(Trait(x=0.0, y=0.0))) is True
    assert entity_satisfies_query(e, Query(Trait(x=0.0, y=0.0, missing=0.0))) is False


def test_entity_satisfies_query_constraint():
    e = make_entity()
    assert entity_satisfies_query(e, Query(Trait(), c.level > 5)) is True
    assert entity_satisfies_query(e, Query(Trait(), c.level > 100)) is False


def test_cursor_reset_after_query():
    e = make_entity()
    entity_satisfies_query(e, Query(Trait(), c.level > 5))
    assert c._obj is None
    entity_satisfies_query(e, Query(Trait(), c.level > 100))
    assert c._obj is None


def test_and_combines_constraints():
    e = make_entity()
    c._obj = e
    combined = and_(c.level > 5, c.count > 3)
    assert combined.eval() is True
    c._obj = None


def test_or_combines_constraints():
    e = make_entity()
    c._obj = e
    combined = or_(c.level > 100, c.count > 3)
    assert combined.eval() is True
    c._obj = None