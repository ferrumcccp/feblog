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
        While FeNode may contain the whole thing, the top-level document nodes
            are "<p>sth</p>" and "sth outside"
    """
    def __init__(self, nodetype = 0):
        """Constructor

        Instance Fields:
        nodetype: Node type
            0 = Source node
            1 = Target node
        _prev: Subtree for data previous to this node (Not currently used)
        _next: Subtree for data next to this node
        _copied: Whether the node is copied and copying subtree is needed
        """
        self._prev = None
        self._next = None
        self._copied = False
        self.size = 1
        self.nodetype = nodetype

    def copy(self):
        """Copy this node

        Note that FeNode is a persistent tree. Copying a node results in the
        node itself actually copied and its subtree marked to be copied on
        access.
        """
        x = self.__class__(nodetype = self.nodetype)
        x._prev = self._prev
        x._next = self._next
        x._copied = True
        self._copied = True
        return x

    def isolate(self):
        """Create a copy with _prev and _next removed

        Not removing other fields. Not even "inside" 
        """
        x = self.copy()
        x._prev = None
        x._next = None
        x.pull_copy()
        return x

    def push_copy(self):
        """Copy the subnode and push down the copy tag"""
        if not self._copied:
            return
        if self._prev:
            self._prev = self._prev.copy()
        if self._next:
            self._next = self._next.copy()
        self._copied = False

    def pull(self):
        """Update subtree-related information

        Update self.size
        """
        self.size = self._prev.size + self._next.size + 1

    def get_prev(self):
        """Get previous node"""
        self.push_copy()
        return self._prev
    def get_next(self):
        """Get next node"""
        self.push_copy()
        return self._next
    def set_prev(self, x):
        """Set previous node, returning new copy"""
        y = self.copy()
        y._prev = x
        return y
    def set_next(self, x):
        """Set next node, returning new copy"""
        y = self.copy()
        y._next = x
        return y

    def __iter__(self):
        """Left-CurrentNode-Right Traverse

        Do not do any of the following things during iteration:
            - Call set_prev or set_next
        """
        for i in self.get_prev():
            yield i
        yield self.isolate()
        for i in self.get_next():
            yield i

    def str_self(self):
        """Get the string repr. of the node itself regardless of prev and next
        """
        return ""

    def __str__(self):
        """Stringify self"""
        return (str(self.get_prev() or "") + self.str_self() 
                + str(self.get_next() or ""))

    def push_back(self, x):
        """Add x to the end of self, returning new node"""
        if self._next == None:
            return self.set_next(x)
        return self.set_next(self.get_next().push_back(x))
    def push_front(self, x):
        """Add x to the beginning of self, returning new node"""
        if self._prev == None:
            return self.set_prev(x)
        return self.set_prev(self.get_prev().push_front(x))

    # I'm too lazy to work on data structure, but I think I can make it into
    # a treap. Then we'll have better performance. Well, XXX


class FeTextNode(FeNode):
    """Text node.
    """
    def __init__(self, text="", nodetype = 0):
        """Constructor

        Instance Fields:
            See super class
            text: Text
        """
        super().__init__(nodetype = nodetype)
        self.text = text

    def str_self(self):
        """Get the string repr. of the node itself regardless of prev and next
        """
        return strescape.amp_escape(self.text)

    def copy(self):
        """Copy this node

        See super class
        """
        cp = super().copy()
        cp.text = self.text
        return cp


class FeTagNode(FeNode):
    """Tag node. That is <xxx zzz="www">yyy</xxx>
    """
    def __init__(self, nodetype = 0, prop = None, tagname = ""):
        """Constructor

        Instance Fields:
            See super class
            prop: dictionary of properties
            tagname: tag name (xxx in the example above)
            __inside: the node embedded inside the tag (yyy)
        """
        super().__init__(nodetype = nodetype)
        self.tagname = tagname
        self._inside = None
        if prop:
            self.prop = prop
        else:
            self.prop = {}

    def copy(self):
        """Copy node
        """
        cp = super().copy()
        cp._inside = self._inside
        cp.prop = {}
        for i in self.prop:
            cp.prop[i] = self.prop[i]
        return cp

    def push_copy(self):
        """Copy the subnode and push down the copy tag"""
        if self._copied and self._inside:
            self._inside = self._inside.copy()
        super().push_copy()

    def get_inside(self):
        self.push_copy()
        return self._inside
    def set_inside(self):
        y = self.copy()
        y._inside = x
        return y

    def str_self(self):
        open_tag = self.tagname
        for i in self.prop:
            if self.prop[i]:
                open_tag += " %s=\"%s\"" % (i,
                        strescape.amp_escape(self.prop[i]))
            else:
                open_tag += " %s" % i
        return "<%s>%s</%s>" % (open_tag,
                str(self.get_inside() or ""), self.tagname)
