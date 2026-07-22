from dataclasses import dataclass, field
import operator
from typing import Any, Callable

def register_unary_op(op):
    def f(self):
        return Constraint(unary_op=op, val1=self)
    return f

def register_bin_op(op):
    def f(self, other):
        if not isinstance(other, c):
            other = Const(other)
        return Constraint(bin_op=op, val1=self, val2=other)
    return f

def not_(self):
    return Constraint(unary_op=lambda ob: not ob, val1=self)

@dataclass
class c:
    _obj: Any = None

    def __hasattr__(self, name):
        return Constraint(lambda o, n: hasattr(o, n), val1=self, val2=Const(name))

    def __getattr__(self, name):
        def get(o, n):
            try:
                return getattr(o, n)
            except AttributeError:
                return False
        return Constraint(bin_op=lambda o, n: get(o, n), val1=self, val2=Const(name))

    def is_(self, other):
        return Constraint(bin_op=lambda ob, ot: ob is ot, val1=self, val2=Const(other))

    def isnot(self, other):
        return Constraint(bin_op=lambda ob, ot: ob is not ot, val1=self, val2=Const(other))

    def eval(self):
        return self._obj

    __add__ = register_bin_op(operator.__add__)
    __radd__ = register_bin_op(operator.__add__)
    __sub__ = register_bin_op(operator.__sub__)
    __rsub__ = register_bin_op(operator.__sub__)
    __mul__ = register_bin_op(operator.__mul__)
    __rmul__ = register_bin_op(operator.__mul__)
    __truediv__ = register_bin_op(operator.__truediv__)
    __rtruediv__ = register_bin_op(operator.__truediv__)
    __floordiv__ = register_bin_op(operator.__floordiv__)
    __rfloordiv__ = register_bin_op(operator.__floordiv__)
    __eq__ = register_bin_op(operator.__eq__)
    __lt__ = register_bin_op(operator.__lt__)
    __gt__ = register_bin_op(operator.__gt__)
    __and__ = register_bin_op(operator.__and__)
    __or__ = register_bin_op(operator.__or__)

@dataclass
class Const:
    val: Any

    def eval(self):
        return self.val

@dataclass
class Constraint:
    unary_op: Callable[[Any], Any] | None = None
    bin_op: Callable[[Any, Any], Any] | None = None
    val1: c | Const | None = None
    val2: c | Const | None = None

    def eval(self):
        if self.val2 is None:
            return self.unary_op(self.val1.eval())
        else:
            return self.bin_op(self.val1.eval(), self.val2.eval())

class Trait:
    def __init__(self, **kwargs):
        self._fields = kwargs

    def __iter__(self):
        for key in self._fields.keys():
            yield key

    def __add__(self, other):
        return self._fields | other._fields


def exattr(trait, name):
    """Exclude a property in a subject_to clause.
    """
    return Constraint(bin_op=lambda o, n: not hasattr(o, n), val1=trait, val2=Const(name))


# Create the "cursor" singleton.
c = c()


def give_traits(*traits: Trait, exclude=None, override=None):
    """Use as a class decorator. Given a dictionary of attribute name to value
    pairs, set attributes of every object to include those as attributes.
    Furthermore, if exclude is supplied, do *not* include those attributes.
    Lastly, if you want to customize the value of an attribute, you may
    override the supplied value with an override dictionary.
    :param attr_vals The attribute to value dictionary.
    :param exclude The attributes to exclude from injection. Defaults to None.
    :param override The attributes to override their default values. Defaults
    to None.
    """
    def wrapper(cls):
        nonlocal exclude
        nonlocal override
        if exclude is None:
            exclude = set()
        if override is None:
            override = dict()
        for trait in traits:
            for attr, val in trait._fields.items():
                if attr not in exclude:
                    if attr not in override:
                        setattr(cls, attr, val)
                    else:
                        setattr(cls, attr, override[attr])
        return cls
    return wrapper


@dataclass
class Query:
    """A class that represnets which attributes and objects should be allowed
    (or disallowed) in a group."""
    and_attr: set[str] = field(default_factory=set)
    constraint: Constraint = None

def entity_satisfies_query(entity, query) -> bool:
    """Check if an entity should (or should not) be added to a particular
    group by analyzing the query structure.

    :param entity: The entity to query.
    :param query: The query to check if the entity can belong to it.
    """
    for attr in query.and_attr:
        if not hasattr(entity, attr):
            return False
    if query.constraint is None:
        return True
    c._obj = entity
    if not query.constraint.eval():
        c._obj = None
        return False
    return True

@dataclass
class World:
    groups: list[tuple[Query, list, list[Callable[[Any, float], None]]]] = \
            field(default_factory=list)

    def push_group(self, query: Query):
        """Add the group and return that group.

        :param query: The query to associate with the group.
        """
        new_group = (query, [], [])
        self.groups.append(new_group)
        return new_group

    def add(self, entity: Any):
        """Add an entity to the world. Under the hood, determines what groups
        the entity should belong to.

        :param entity: The entity to add to the world.
        """
        for query, group, funcs in self.groups:
            if entity_satisfies_query(entity, query):
                group.append(entity)

    def extend(self, entities: list[Any]):
        """Add a collection of entities to the world.

        :param entities: The collection of entities to add to the world.
        """
        for entity in entities:
            self.add(entity)

    def update(self, dt: float):
        """Update the world (and all the corresponding groups/entities).

        :param dt: The amount of time that elapsed. (Common for videogame 
           applications)
        """
        for _, group, funcs in self.groups:
            for func in funcs:
                for entity in group:
                    func(entity, dt)


def requirements(world: World, 
                 require: Trait,
                 subject_to: Constraint | None=None):
    """Use as a decorator, runs the decorated function on each entity that
    has the required components and none of the excluded components (or
    excluded objects).

    :param require: Required attribute for an entity to be ran.
    :subject_to: A Constraint object that the object must satisfy.
    """
    def req_dec(func):
        query = Query(require, subject_to)
        group = world.push_group(query)
        def inner(e, dt):
            return func(e, dt)
        group[2].append(inner)
        return inner
    return req_dec

def one_shot(world: World, 
             require: Trait,
             subject_to: Constraint | None=None):
    """Use as a decorator. Suppose you have a function `f(e)` that operates on
    some entity and you decorate it with one_shot. The returned function
    takes no parameters and when called it is applied to every entity that
    satisfies the query declared in the one_shot decorator. This contrasts
    with the requirements decorator, because requirements causes all 
    decorated functions to invoke when `update` is called.

    :param require: Required attribute for an entity to be ran.
    :param subject_to: A Constraint object that the object must satisfy.
    """
    def req_dec(func):
        query = Query(require, subject_to)
        group = world.push_group(query)
        def inner():
            for entity in group[1]:
                func(entity)
        return inner
    return req_dec
