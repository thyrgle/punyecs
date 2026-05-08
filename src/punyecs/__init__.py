from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Query:
    """A class that represnets which attributes and objects should be allowed
    (or disallowed) in a group."""
    and_attr: set[str] = field(default_factory=set)
    exclude_attr: set[str] = field(default_factory=set)
    exclude_obj: set[Any] = field(default_factory=set)


@dataclass
class World:
    groups: list[(Query, list, list[Callable[[Any, float], None]])] = \
            field(default_factory=list)

    def entity_satisfies_query(self, entity, query) -> bool:
        """Check if an entity should (or should not) be added to a particular
        group by analyzing the query structure."""
        for e in query.exclude_obj:
            if entity == e:
                return False
        for attr in query.and_attr:
            if not hasattr(entity, attr):
                return False
        for attr in query.exclude_attr:
            if hasattr(entity, attr):
                return False
        return True

    def push_group(self, query: Query):
        """Add the group and return that group."""
        new_group = (query, [], [])
        self.groups.append(new_group)
        return new_group

    def add(self, entity: Any):
        """Add an entity to the world. Under the hood, determines what groups
        the entity should belong to."""
        for query, group, funcs in self.groups:
            if self.entity_satisfies_query(entity, query):
                group.append(entity)

    def update(self, dt: float):
        """Update the world (and all the corresponding groups/entities)."""
        for _, group, funcs in self.groups:
            for func in funcs:
                for entity in group:
                    func(entity, dt)


def requirements(world, require: list[str],
                 exclude: list[str]=None, exclude_obj: list[Any]=None,
                 *args, **kwargs):
    """Use as a decorator, runs the decorated function on each entity that
    has the required components and none of the excluded components (or
    excluded objects).

    :param require: Required attribute for an entity to be ran.
    :param exclude: Entity must *not* have the following attributes.
    :param exclude_obj: Exculde individual objects from being ran.
    """
    def req_dec(func):
        nonlocal exclude
        nonlocal exclude_obj
        exclude = exclude or []
        exclude_obj = exclude_obj or []
        query = Query(require, exclude, exclude_obj)
        group = world.push_group(query)
        group[2].append(func)
        def inner(func):
            return func()
        return inner
    return req_dec

def query(world: World, query: Query, *args, **kwarg):
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
        print(world.groups)
        return inner
    return query_dec
