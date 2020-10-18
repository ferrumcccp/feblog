""" Node tree

Tree structure to free the blog system from the dull string processing
"""

import random

import strescape


class FeNode:
    """A node storing a series of BBCode and HTML

    To make things clear, when we speak about a "node", we mean a data
    structure object which contains a series of elements, or in other words,
    a valid segment of the document. An "element", on the other hand, means
    a document element, either a piece of plain text or a tag with all of its
    inner content. (The document sometimes refers to elements as "nodes", FIXME)
    
    **It's recommended to use operators helper functions in place of constructors and member methods**

    Since nodes are not elements, the differences between FeNode, FeTextNode
    and FeTagNode is just a matter of implementation detail. The member methods
    also cover too many details. Besides, the data structure is designed to
    work like a value type. Member methods are not what it's really about.

    (TODO: work on helper functions)
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
        x._rand = self._rand
        x.size = self.size
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
        """Get the str of the node itself, ignoring prev and next
        """
        return ""

    def __str__(self):
        """Stringify self"""
        return (str(self.get_prev() or "") + self.str_self()
                + str(self.get_next() or ""))

    def repr_self(self):
        """Get the repr of the node itself, ignoring prev and next
        """
        return "<FeNode>"

    def __repr__(self):
        """Represent self"""
        return "(%s) + %s + (%s)" % (repr(self.get_prev()), self.repr_self()
                , repr(self.get_next()))

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

    def repr_self(self):
        return repr(self.text)


class FeTagNode(FeNode):
    """Tag node. That is <xxx zzz="www">yyy</xxx>
    """
    def __init__(self, tagname = "", prop = None, inside = None, nodetype = 0):
        """Constructor

        Instance Fields:
            See super class
            prop: dictionary of properties
                "key":"string value" means a property with value
                    (e.g <sometag href="#top">)
                "key":None means a key-only property
                    (e.g <sometag contenteditable>)
                If key is "self", it means that the tagname itself 
                    has theproperty value with it 
                    e.g. [url="about:blank"]

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

    def get_inside(self):
        """get the node inside the tag

        Only to be used when the node represents only one
        toplevel tag. (e.g the item created by iteration)
        Otherwise you'll never know how it is actually 
        stored."""
        self.push_copy()
        return self._inside

    def str_self(self):
        open_tag = self.tagname
        if "self" in self.prop:
            open_tag += "=%s" % self.prop["self"]
        for i in self.prop:
            if self.prop[i]:
                if i == "self":
                    pass
                else:
                    open_tag += " %s=\"%s\"" % (i,
                        strescape.amp_escape(self.prop[i]))
            else:
                open_tag += " %s" % i
        fmt = "<%s>%s</%s>" if self.nodetype else "[%s]%s[/%s]"
        return fmt % (open_tag,
                str(self.get_inside() or ""), self.tagname)

    def repr_self(self):
        return ("FeTagNode(tagname = %s, prop = %s, inside = %s, nodetype = %d, size = %d, _rand = %.2e)"
                % (repr(self.tagname), repr(self.prop), repr(self._inside), self.nodetype, self.size, self._rand))


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
        # print("w = %s" % repr(w))
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

    def test_debug(self):
        """A test to fix the incorrect maintenance of size, hope this works."""
        x = FeTagNode("x" , {})
        # print(repr(x))
        y = x
        self.assertEqual(x.size, 1)
        x = x + y
        # print(repr(x))
        self.assertEqual(x.size, 2)
        x = x + y
        # print(repr(x))
        self.assertEqual(x.size, 3)
        x = x + y
        # print(repr(x))
        self.assertEqual(x.size, 4)
        x = x + y
        # print(repr(x))
        self.assertEqual(x.size, 5)


if __name__ == '__main__':
    #random.seed(5) # For debugging
    unittest.main()
