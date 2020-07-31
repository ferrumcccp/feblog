

class FeNode:
    """
    A node storing a series of BBCode and HTML

    This class stores a data structure node which can be several document nodes.
    For example:
        <p>sth</p>sth outside
    hmm
    """
    def __init__(self, nodetype = 0):
        """Constructor

        Instance Fields:
        nodetype: Node type
            0 = BBCode
            1 = Target HTML
        __prev: Subtree for data previous to this node (Not currently used)
        __next: Subtree for data next to this node
        __copied: Whether the node is copied and copying subtree is needed
        """
        self.__prev = None
        self.__next = None
        self.__copied = False
        self.nodetype = nodetype

    def copy(self):
        """Copy this node

        Note that FeNode is a persistent tree. Copying a node results in the
        node itself actually copied and its subtree marked to be copied on
        access.
        """
        x = FeNode(nodetype = self.nodetype)
        x.__prev = self.__prev
        x.__next = self.__next
        x.__copied = 1
        self.__copied = 1

    def push_copy(self):
        """Copy the subnode and push the copy mark down"""
        self.__prev = self.__prev.copy()


