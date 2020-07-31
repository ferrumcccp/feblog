"""
FeBlog - Ferrumcccp's blog system

TODO: this is a work in progress.

As a student who loves home-made blog systems, I've worked out two
blog systems previously. The first one is a few helper functions in
PHP. The second one is based on a rather buggy BBCode parser written
in JS. Here are the goals of this project:
    1. Allow a mixture of Markdown and BBCode.
    2. Detect markup code automatically as well as support manual control with
        HTML escape.
    3. Generate document in tree structure and then stringify the tree, rather
        than directly join strings.
    4. Support a more flexible interface.
    5. With the interface, implement menu bars, the index page, contents etc.

Definitions:
    1. source node: a node read from BBCode/Markdown documents or virtual,
        auxiliary nodes created by the program.
    2. target node: HTML nodes to be written.
The project shall consist of:
    1. A persistent (for easy copying) tree of document objects.
    2. Main classes and functions.
    3. A parser.
    4. "Renderer"s that render each source node as a target node.
    5. "Decorator"s that decorate the results from renderers.
        Results from renderers and decorators may contain other source nodes,
        which will be rerendered until all nodes are target nodes.
        This shall allow template-like reusability.
    6. "GlobalGenerator"s that generate content pages, including the index page
        , categories etc.
    7. "GlobalDecorator"s that decorate whole pages.
"""
from . import nodetree
