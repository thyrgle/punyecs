from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Query:
    """A class that represnets which attributes and objects should be allowed
    (or disallowed) in a group."""
    and_attr: set[str] = set()
    exclude_attr: set[str] = set()
    exclude_obj: set[Any] = set()


@dataclass
class World:
    groups: list[(Query, set, list[Callable[[Any, float]]])] = []

    def entity_satisfies_query(entity, query) -> bool:
        """Check if an entity should (or should not) be added to a particular
        group by analyzing the query structure."""
        if entity in query.exclude_obj:
            return False
        for attr in query.and_attr:
            if not hasattr(entity):
                return False
        for attr in query.exclude_attr:
            if hasattr(entity):
                return False
        return True

    def push_group(self, query: Query):
        """Add the group and return that group."""
        new_group = (query, set(), [])
        self.groups.append(new_group)
        return new_group

    def add(self, entity: Any):
        """Add an entity to the world. Under the hood, determines what groups
        the entity should belong to."""
        for query, group, funcs in self.groups:
            if self.entity_satisfies_query(entity, query):
                group.add(entity)

    def update(self, dt: float):
        """Update the world (and all the corresponding groups/entities)."""
        for _, group, funcs in self.groups:
            for func in funcs:
                for entity in group:
                    func(entity, dt)


def query(world, require: list[str],
          exclude: list[str]=None, exclude_obj: list[Any]=None):
    """Use as a decorator, runs the decorated function on each entity that
    has the required components and none of the excluded components (or
    excluded objects).

    :param require: Required attribute for an entity to be ran.
    :param exclude: Entity must *not* have the following attributes.
    :param exclude_obj: Exculde individual objects from being ran.
    """
    exclude = exclude or []
    exclude_obj = exclude_obj or []
    query = Query(require, exclude, exclude_obj)
    group = world.add_group(query)
    def inner(func):
        group[2].append(func)
        return func()
    return inner
