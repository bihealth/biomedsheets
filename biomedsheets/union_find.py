# -*- coding: utf-8 -*-
"""Union-find data structure"""


class UnionFind:
    """Union-find data structure.

    Each unionFind instance X maintains a family of disjoint sets of
    hashable objects, supporting the following two methods:

    - X[item] returns a name for the set containing the given item.
      Each set is named by an arbitrarily-chosen one of its members; as
      long as the set remains unchanged it will keep the same name. If
      the item is not yet part of a set in X, a new singleton set is
      created for it.

    - X.union(item1, item2, ...) merges the sets containing each item
      into a single larger set.  If any item is not yet part of a set
      in X, it is added to X as one of the members of the merged set.

    Adapted from https://www.ics.uci.edu/~eppstein/PADS/UnionFind.py

    Copyright (c) 2002-2015, David Eppstein
    """

    def __init__(self):
        """Create a new empty union-find structure"""
        self.weights = {}
        self.parents = {}

    def __getitem__(self, key):
        """Find and return the name of the set containing the key"""

        # check for previously unknown key
        if key not in self.parents:
            self.parents[key] = key
            self.weights[key] = 1
            return key

        # find path of keys leading to the root
        path = [key]
        root = self.parents[key]
        while root != path[-1]:
            path.append(root)
            root = self.parents[root]

        # compress the path and return
        for ancestor in path:
            self.parents[ancestor] = root
        return root

    def __iter__(self):
        """Iterate through all items ever found or unioned by this structure
        """
        return iter(self.parents)

    def union(self, *keys):
        """Find the sets containing the keys and merge them all"""
        roots = [self[x] for x in keys]
        heaviest = max([(self.weights[r], r) for r in roots])[1]
        for r in roots:
            if r != heaviest:
                self.weights[heaviest] += self.weights[r]
                self.parents[r] = heaviest
