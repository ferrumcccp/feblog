"""Functions to escape strings
"""


def amp_escape(s):
    """& escape

    Example:
    >>> amp_escape("<XRJ is HUGE>\\\"&")
    '&lt;XRJ&nbsp;is&nbsp;HUGE&rt;&quot;&amp;'
    """
    t = ""
    mp = {"<": "&lt;", ">": "&rt;", '"': "&quot;", " ":"&nbsp;"
            ,"&": "&amp;"}
    for i in s:
        if i in mp:
            t += mp[i]
        else:
            t += i
    return t


if __name__ == "__main__":
    import doctest
    doctest.testmod()
