
# define data types to be used by different modules
# TODO: I don't like this approach, maybe just define tuples where necessary in each file
from collections import namedtuple
Point = namedtuple('Point', 'x y')
Vertex = namedtuple('Vertex', 't x y')
Event = namedtuple('Event', 't x y p')