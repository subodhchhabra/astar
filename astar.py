import heapq
import math
import time


maze_path = "maze.txt"
search_max_iter = 9999


def euclidian(a, b):
    return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2)


def cost(a, b):
    return euclidian(a, b)


def heuristic(a, b):
    return euclidian(a, b)


class Node:
    def __init__(self, x, y, parent, goal):
        self.x = x
        self.y = y
        self.parent = parent

        if(parent is None):
            self.g = 0
        else:
            self.g = cost(parent, self) + parent.g

        if(goal is None):
            self.h = 0
        else:
            self.h = heuristic(goal, self)

        self.f = self.g + self.h

    def key(self):
        return self.x << 16 + self.y

    def __hash__(self):
        return self.x << 16 + self.y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        if(self.f == other.f):
            return self.g < other.g
        return self.f < other.f


class PriorityQueue:
    def __init__(self):
        self.q = []
        self.m = {}

    def push(self, item):
        if(item.key() in self.m):
            if(item < self.m[item.key()]):
                k = self.m[item.key()]
                print('q', len(self.q))
                print('m', len(self.m))
                for n, i in enumerate(self.q):
                    print(n, i.x, i.y)
                for k in self.m:
                    print(k, self.m[k].x, self.m[k].y)
                print('k', k.x, k.y)
                self.q.remove(k)
                del self.m[item.key()]
                print('q', len(self.q))
                print('m', len(self.m))
                raise Exception('hit')
                heapq.heapify(self.q)

        heapq.heappush(self.q, item)
        self.m[item.key()] = item

    def pop(self):
        return heapq.heappop(self.q)

    def size(self):
        return len(self.q)


class Astar:
    def __init__(self, start, goal, isInBounds, cap=None):
        self.closedset = set()
        self.currentSet = set()
        self.openset = PriorityQueue()
        self.openset.push(start)
        self.checkBounds = isInBounds
        self.counter = 0

    def search(self):
        current_node = self.openset.pop()
        self.counter += 1
        if current_node == goal:
            return True, current_node, current_node.g, self.counter

        self.closedset.add(current_node)

        x = current_node.x
        y = current_node.y

        neighbors = [
            Node(x+1, y, current_node, goal),
            Node(x, y-1, current_node, goal),
            Node(x-1, y, current_node, goal),
            Node(x, y+1, current_node, goal),
            Node(x+1, y-1, current_node, goal),
            Node(x-1, y-1, current_node, goal),
            Node(x-1, y+1, current_node, goal),
            Node(x+1, y+1, current_node, goal),
        ]

        for i in neighbors:
            if(self.checkBounds(i.x, i.y) and i not in self.closedset):
                self.openset.push(i)

        return False, current_node, current_node.g, self.counter


class Field:
    def __init__(self, path):
        with open(path) as f:
            self.maze = f.readlines()

        self.rows = len(self.maze)
        if(self.rows < 3):
            raise Exception('invalid maze')
        self.cols = len(self.maze[0]) - 1
        if(self.cols < 3):
            raise Exception('invalid maze')

    def toString(self, openset, closedset, path=None):
        nmaze = self.maze[:]

        for i in range(self.rows):
            nmaze[i] = nmaze[i].replace('#', u'\u2592').replace('.', ' ')

        for node in closedset:
            k = list(nmaze[node.y])
            k[node.x] = '.'
            nmaze[node.y] = ''.join(k)

        for node in openset.q:
            k = list(nmaze[node.y])
            k[node.x] = 'O'
            nmaze[node.y] = ''.join(k)

        while(path is not None):
            k = list(nmaze[path.y])
            k[path.x] = u'\u2588'
            nmaze[path.y] = ''.join(k)
            path = path.parent

        return ''.join(nmaze)


maze = Field(maze_path)


def isInMazeBounds(x, y):
    return maze.maze[y][x] != '#'


goal = Node(maze.cols - 2, maze.rows - 2, None, None)
start = Node(1, 1, None, goal)

s = Astar(start, goal, isInMazeBounds, 9999)

while(s.openset.size() > 0 and
        (search_max_iter is None or s.counter < search_max_iter)):
    done, node, node_g, counter = s.search()
    print(maze.toString(s.openset, s.closedset, node))
    print("iterations: {}  cost: {}".format(counter, node_g))
    if(done):
        break
    time.sleep(0.02)


# for i, v in enumerate(maze.maze):
#     print(i, v)

# end = Node(9, 9, None, None)
# node1 = Node(0, 0, None, end)
# node2 = Node(1, 0, node1, end)
# node3 = Node(2, 0, node2, end)
# node4 = Node(2, 1, node3, end)
# node5 = Node(2, 0, node4, end)
# node6 = Node(2, 2, node4, end)
# node7 = Node(3, 2, node6, end)
#
# openset = PriorityQueue()
#
# openset.push(node1.as_tuple())
# openset.push(node2.as_tuple())
# openset.push(node3.as_tuple())
# openset.push(node4.as_tuple())
# openset.push(node5.as_tuple())
# openset.push(node6.as_tuple())
# openset.push(node7.as_tuple())
#
# while openset.size() > 0:
#     f, g, i = openset.pop()
#     print(f, g)
