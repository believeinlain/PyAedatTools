
# define data types to be used by different modules
from collections import namedtuple
Point = namedtuple('Point', 'x y')
Vertex = namedtuple('Vertex', 't x y')
Event = namedtuple('Event', 't x y p')