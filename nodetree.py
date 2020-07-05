class FeNode:
    """
    A node storing a series of BBCode and HTML

    This class stores a data structure node which can be several document nodes. For example:
        <p>sth</p>sth outside
    hmm
    """
    def __init__(self):
        self.prev = None
        self.next = None
