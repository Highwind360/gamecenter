"""
structures.py
Grayson Sinclair

A module to contain data structures used by the game.
"""

from collections import deque


class UpTreeNode():
    def __init__(self, value, next_node=None):
        self.value = value
        self.next_node = next_node
        self.treeheight = 1
        if self.next_node != None:
            root = next_node.find()
            root.treeheight += self.treeheight

    def find(self):
        """Returns the root value of the tree the node belongs to.
        After finding the root, it performs compression on the tree."""
        if self.next_node == None:
            return self
        else:
            root = self.next_node.find()
            self.next_node = root # compression
            return root

    def union(self, other):
        """Unions the other node to this one.
        For performance reasons, it trusts that other is a root.
        If other is not a root, it may unintentionally prune another tree."""
        other.next_node = self
        self.treeheight += other.treeheight

class DisjointSet():
    """Classic implementation of a disjoint set."""

    def __init__(self, items = []):
        self.items = {item:UpTreeNode(item) for item in items}
        self.size = len(self.items.keys())

    def add(self, item, children=[]):
        """Adds a new item to the collection of sets.

        item - the item to be added
        children - any additional items for the original to be grouped with."""
        if item in self.items.keys():
            raise ValueError("Item already exists in collection.")
        item_node = UpTreeNode(item)
        self.items[item] = item_node
        self.size += 1

        for item_child in children:
            child_node = self.add(item_child)
            self.union(child_node, item_node)

        return item_node

    def union(self, item1, item2):
        """Blindly unions two items together by height.
        Unless you know what you're doing, it's recommended to use union-find."""
        if item1 not in self.items.keys() or item2 not in self.items.keys():
            raise ValueError("Item does not exist in the collection.")
        node1 = self.items[item1]
        node2 = self.items[item2]
        if node1.treeheight >= node2.treeheight:
            node1.union(node2)
        else:
            node2.union(node1)
        self.size -= 1

    def union_find(self, item1, item2):
        """Finds the two items' representative nodes and unions them."""
        root1 = self.find(item1)
        root2 = self.find(item2)
        self.union(root1, root2)

    def find(self, item):
        """Finds an item in the set, with path compression."""
        if item not in self.items.keys():
            raise ValueError("Item does not exist in the collection.")
        else:
            return self.items[item].find().value
