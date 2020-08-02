""" Node tree

Tree structure to free the blog system from the dull string processing
"""
import strescape

class FeNode:
    """A node storing a series of BBCode and HTML

    Each instance stores a data structure node which can be several document
        nodes.
    For example:
        <p>sth</p>sth outside
    hmm
    """
    def __init__(self, nodetype = 0):
        """Constructor

        Instance Fields:
        nodetype: Node type
            0 = Source node
            1 = Target node
        __prev: Subtree for data previous to this node (Not currently used)
        __next: Subtree for data next to this node
        __copied: Whether the node is copied and copying subtree is needed
        """
        self.__prev = None
        self.__next = None
        self.__copied = False
        self.size = 1
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
        """Copy the subnode and push down the copy tag"""
        self.__prev = self.__prev.copy()
        self.__next = self.__next.copy()
        self.__copied = 0

    def pull(self):
        """Update subtree-related information

        Update self.size
        """
        self.size = self.__prev.size + self.__next.size + 1

    def get_prev(self):
        self.push_copy()
        return self.__prev
    def get_next(self):
        self.push_copy()
        return self.__next
    def set_prev(self, x):
        self.push_copy()
        self.__prev = x
        self.pull()
    def set_next(self, x):
        self.push_copy()
        self.__next = x
        self.pull()

    def __iter__(self):
        """Left-CurrentNode-Right Traverse

        Do not do any of the following things during iteration:
            - Call set_prev or set_next
        """
        for i in self.get_prev():
            yield i
        yield self
        for i in self.get_next():
            yield i

    def str_self(self):
        """Get the string repr. of the node itself regardless of prev and next
        """
        return ""

    def __str__(self):
        return str(self.get_prev()) + self.str_self() + str(self.get_next())


class FeTextNode(FeNode):
    """Text node
    """
    def __init__(self, text="", nodetype = 0):
        """Constructor

        Instance Fields:
            See super class
            text: Text
        """
        super().__init__()
        self.text = text

    def str_self(self):
        """Get the string repr. of the node itself regardless of prev and next
        """
        return amp_escape(self.text)

    def copy(self):
        """Copy this node

        See super class
        """
        cp = super().copy()
        cp.text = self.text
