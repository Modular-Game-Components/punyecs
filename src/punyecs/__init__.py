from dataclasses import dataclass, field
from typing import Any, Callable


def inject_attrs(attrs_val: dict[str, Any], exclude=None, override=None):
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
        for attr, val in attrs_val.items():
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
    exclude_attr: set[str] = field(default_factory=set)
    exclude_objs: list[Any] = field(default_factory=list)
    exclude_attr_vals: dict[str, Any] = field(default_factory=dict)
    exclude_attr_funcs: dict[str, Callable[[Any], bool]] = \
        field(default_factory=dict)

def entity_satisfies_query(entity, query) -> bool:
    """Check if an entity should (or should not) be added to a particular
    group by analyzing the query structure.

    :param entity: The entity to query.
    :param query: The query to check if the entity can belong to it.
    """
    for e in query.exclude_objs:
        if entity == e:
            return False
    for attr in query.and_attr:
        if not hasattr(entity, attr):
            return False
    for attr in query.exclude_attr:
        if hasattr(entity, attr):
            return False
    for attr, val in query.exclude_attr_vals.items():
        if hasattr(entity, attr) and getattr(entity, attr) == val:
            return False
    for attr, f in query.exclude_attr_funcs.items():
        if hasattr(entity, attr) and f(getattr(entity, attr)):
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
                 require: set[str],
                 exclude: set[str] | None=None, 
                 exclude_objs: list[Any] | None=None,
                 exclude_attr_vals: dict[str, Any] | None = None,
                 exclude_attr_funcs: dict[str, Callable[[Any], bool]] | None =\
                    None):
    """Use as a decorator, runs the decorated function on each entity that
    has the required components and none of the excluded components (or
    excluded objects).

    :param require: Required attribute for an entity to be ran.
    :param exclude: Entity must *not* have the following attributes.
    :param exclude_objs: Exculde individual objects from being ran.
    :param exclude_attr_vals: Exclude objects that have an attribute with a
       particular value.
    :param exclude_attr_funcs: Exclude objects whose attributes do not satisfy
       certain predicates.
    """
    exclude = exclude or set()
    exclude_objs = exclude_objs or []
    exclude_attr_vals = exclude_attr_vals or {}
    def req_dec(func):
        query = Query(require, exclude, exclude_objs, exclude_attr_vals)
        group = world.push_group(query)
        def inner(e, dt):
            return func(e, dt)
        group[2].append(inner)
        return inner
    return req_dec

def one_shot(world: World, 
             require: set[str],
             exclude: set[str] | None=None, 
             exclude_objs: list[Any] | None=None,
             exclude_attr_vals: dict[str, Any] | None = None,
             exclude_attr_funcs: dict[str, Callable[[Any], bool]] | None =\
             None):
    """Use as a decorator. Suppose you have a function `f(e)` that operates on
    some entity and you decorate it with one_shot. The returned function
    takes no parameters and when called it is applied to every entity that
    satisfies the query declared in the one_shot decorator. This contrasts
    with the requirements decorator, because requirements causes all 
    decorated functions to invoke when `update` is called.

    :param require: Required attribute for an entity to be ran.
    :param exclude: Entity must *not* have the following attributes.
    :param exclude_objs: Exculde individual objects from being ran.
    :param exclude_attr_vals: Exclude objects that have an attribute with a
       particular value.
    :param exclude_attr_funcs: Exclude objects whose attributes do not satisfy
       certain predicates.
    """
    exclude = exclude or set()
    exclude_objs = exclude_objs or []
    exclude_attr_vals = exclude_attr_vals or {}
    def req_dec(func):
        query = Query(require, exclude, exclude_objs, exclude_attr_vals)
        group = world.push_group(query)
        def inner():
            for entity in group[1]:
                func(entity)
        return inner
    return req_dec

def query(world: World, query: Query):
    """Use as a decorator, runs the decorated function on each entity that
    satisfy the query object (similar to ``requirements`` but takes in a 
    Query object directly. ``requirements`` builds a query object.

    :param world: World to query over.
    :param query: Query to execute against.
    """
    def query_dec(func):
        group = world.push_group(query)
        def inner(e, dt):
            return func(e, dt)
        group[2].append(inner)
        return inner
    return query_dec
