""" Node tree

Tree structure to free the blog system from the dull string processing
"""

import random

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
        _rand: Random weight for maintaining tree structure
        """
        self._prev = None
        self._next = None
        self._copied = False
        self.size = 1
        self.nodetype = nodetype
        self._rand = random.randint(0, 9223372036854775807)

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
        x.pull()
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
        self.size = 1
        if self._prev:
            self.size += self._prev.size
        if self._next:
            self.size += self._next.size

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
        y.pull()
        return y
    def set_next(self, x):
        """Set next node, returning new copy"""
        y = self.copy()
        y._next = x
        y.pull()
        return y

    def __iter__(self):
        """Left-CurrentNode-Right Traverse

        Do not do any of the following things during iteration:
            - Call set_prev or set_next
        """
        for i in self.get_prev() or []:
            yield i
        yield self.isolate()
        for i in self.get_next() or []:
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
        if x and x._rand < self._rand:
             return x.push_front(self)

        if self._next == None:
            return self.set_next(x)

        return self.set_next(self.get_next().push_back(x))

    def push_front(self, x):
        """Add x to the beginning of self, returning new node"""
        if x and x._rand < self._rand:
            return x.push_back(self)

        if self._prev == None:
            return self.set_prev(x)

        return self.set_prev(self.get_prev().push_front(x))

    def __add__(self, x):
        """Operator form of push_back which makes life easier"""
        if not isinstance(x, FeNode):
            x = FeTextNode(str(x), nodetype = self.nodetype)
        return self.push_back(x)

    def __radd__(self, x):
        """Operator form of push_front which makes life easier"""
        if not isinstance(x, FeNode):
            x = FeTextNode(str(x), nodetype = self.nodetype)
        return self.push_front(x)

    def split_at(self, k):
        """Split the node into two nodes: 0~(k-1)th and the rest

        returns a pair"""
        if k <= 0:
            return None, self.copy()

        if k >= self.size:
            return self.copy(), None

        if self._prev and k <= self._prev.size:
            x, y = self.get_prev().split_at(k)
            return x, self.set_prev(y)
        else:
            lt_size = 0
            if self._prev:
                lt_size = self._prev.size
            x, y = self.get_next().split_at(k - lt_size - 1)
            return self.set_next(x), y


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

    def get_text(self):
        """Get text"""
        return self.text
    
    def set_text(self, text):
        """Set text and return new copy"""
        cp = self.copy()
        cp.text = text
        return cp

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
    def __init__(self, tagname = "",prop = None, inside = None, nodetype = 0):
        """Constructor

        Instance Fields:
            See super class
            prop: dictionary of properties
                "key":"string value" means a property with value
                    (e.g <sometag href="#top">)
                "key":None means a key-only property
                    (e.g <sometag contenteditable>)

            tagname: tag name (xxx in the example above)
            _inside("inside" as in arg):
                the node embedded inside the tag (yyy)
        """
        super().__init__(nodetype = nodetype)
        self.tagname = tagname
        self._inside = inside
        if prop:
            self.prop = prop
        else:
            self.prop = {}

    def copy(self):
        """Copy node
        """
        cp = super().copy()
        cp._inside = self._inside
        cp.tagname = self.tagname
        cp.prop = {}
        for i in self.prop:
            cp.prop[i] = self.prop[i]
        return cp

    def push_copy(self):
        """Copy the subnode and push down the copy tag"""
        if self._copied and self._inside:
            self._inside = self._inside.copy()
        super().push_copy()

    def __get_inside(self):
        """set the node inside the tag

        See set_inside for usage notes."""
        self.push_copy()
        return self._inside

    def str_self(self):
        open_tag = self.tagname
        for i in self.prop:
            if self.prop[i]:
                open_tag += " %s=\"%s\"" % (i,
                        strescape.amp_escape(self.prop[i]))
            else:
                open_tag += " %s" % i
        fmt = "<%s>%s</%s>" if self.nodetype else "[%s]%s[/%s]"
        return fmt % (open_tag,
                str(self.__get_inside() or ""), self.tagname)


import unittest
class FeNodeTest(unittest.TestCase):
    def test_test1(self):
        """Basic Test"""
        x = FeTagNode(tagname = "x", prop = {"y": "1", "z": None})
        z = x.copy()
        self.assertEqual(str(x), '[x y="1" z][/x]')
        self.assertEqual(str(z), '[x y="1" z][/x]')
        u = x.push_back(FeTextNode(text = "hahaha"))
        self.assertEqual(str(u), '[x y="1" z][/x]hahaha')
        v=x.push_front(FeTextNode(text = "ohmygod"))
        self.assertEqual(str(v), 'ohmygod[x y="1" z][/x]')
        w=u.push_front(FeTextNode(text = "ohmygod"))
        self.assertEqual(str(w), 'ohmygod[x y="1" z][/x]hahaha')
        # The original x should be unchanged.
        self.assertEqual(str(x), '[x y="1" z][/x]')
        # Iteration
        self.assertListEqual([str(i) for i in w], ['ohmygod'
            , '[x y="1" z][/x]'
            , 'hahaha'])
        # Let's see if size is correct
        self.assertEqual(w.size, 3)
        # Splitting
        w1, w2 = w.split_at(2)
        self.assertEqual(str(w1), 'ohmygod[x y="1" z][/x]')
        self.assertEqual(str(w2), 'hahaha')
        # Merging again, this time using the + operator
        w = 1 + (w1 + w2 + "s")
        self.assertEqual(str(w), '1ohmygod[x y="1" z][/x]hahahas')

    def test_test2(self):
        """ "inside" field test as well as tricky tests."""
        x = FeTagNode("x", {"y": "1", "z": None}, nodetype = 1)
        xstr = x.push_back(FeTextNode("xrjakioi"))
        y = FeTagNode(tagname = "y", inside = xstr)
        self.assertEqual(str(y), '[y]<x y="1" z></x>xrjakioi[/y]')
        # Trick: push back its inner content
        y = y.push_back(xstr)
        self.assertEqual(str(y), '[y]<x y="1" z></x>xrjakioi[/y]<x y="1" z></x>xrjakioi')
        # Trick: push itself back
        # Since nodes are copied, y should be repeated only twice
        y = y.push_back(y)
        self.assertEqual(str(y), '[y]<x y="1" z></x>xrjakioi[/y]<x y="1" z></x>xrjakioi[y]<x y="1" z></x>xrjakioi[/y]<x y="1" z></x>xrjakioi')
        # Let's see if size is correct
        self.assertEqual(y.size, 6)


if __name__ == '__main__':
    random.seed(1) # For debugging
    unittest.main()
