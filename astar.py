# astar.py [mazefile] [delay]
#
# 'mazefile' allows you to specify a custom maze.
# 'delay' is the delay between steps in milliseconds.

import curses, signal, sys
import heapq, math


# heuristics
def euclidean(a, b):
    return math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2)

def manhattan(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)

maze_fname = "maze.txt"  # default maze name
delay_ms = 50            # default number of milliseconds to wait
heuristic = euclidean    # specify which herusitic to use
cost = euclidean         # don't change this


class Node:
    def __init__(self, x, y, parent, goal):
        self.x = x
        self.y = y
        self.parent = parent

        if parent is None:
            self.g = 0
        else:
            self.g = cost(parent, self) + parent.g

        if goal is None:
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
        if self.f == other.f:
            return self.g < other.g
        return self.f < other.f


class PriorityQueue:
    def __init__(self):
        self.q = []
        self.m = {}

    def push(self, item):
        if item.key() in self.m:
            if item < self.m[item.key()]:
                self.q.remove(self.m[item.key()])
                del self.m[item.key()]
                heapq.heapify(self.q)
                heapq.heappush(self.q, item)
                self.m[item.key()] = item
        else:
            heapq.heappush(self.q, item)
            self.m[item.key()] = item

    def pop(self):
        k = heapq.heappop(self.q)
        del self.m[k.key()]
        return k

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
            if self.checkBounds(i.x, i.y) and i not in self.closedset:
                self.openset.push(i)

        return False, current_node, current_node.g, self.counter


class Field:
    def __init__(self, path):
        with open(path) as f:
            self.maze = f.readlines()

        self.rows = len(self.maze)
        if self.rows < 3:
            raise RuntimeError('invalid maze')
        self.cols = len(self.maze[0]) - 1
        if self.cols < 3:
            raise RuntimeError('invalid maze')

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

        while path is not None:
            k = list(nmaze[path.y])
            k[path.x] = u'\u2588'
            nmaze[path.y] = ''.join(k)
            path = path.parent

        return ''.join(nmaze)

    def isInBounds(self, x, y):
        return self.maze[y][x] != '#'



if __name__ == '__main__':
    # parse args
    if len(sys.argv) >= 2:
        maze_fname = sys.argv[1]
        if len(sys.argv) == 3:
            delay_ms = int(sys.argv[2])

    maze = Field(maze_fname)
    goal = Node(maze.cols - 2, maze.rows - 2, None, None)
    start = Node(1, 1, None, goal)
    s = Astar(start, goal, maze.isInBounds, 9999)
    success = False

    # curses setup
    def exit_gracefully(*_):
        curses.endwin()
        sys.exit()

    curses.initscr()
    curses.noecho()
    win = curses.newwin(maze.rows+10, maze.cols+10)
    signal.signal(signal.SIGINT, exit_gracefully)

    # run astar
    while s.openset.size() > 0:
        done, node, node_g, counter = s.search()

        # output to curses
        win.erase()
        win.addstr(maze.toString(s.openset, s.closedset, node))
        win.addstr("iterations: {:<6}\n".format(counter))
        win.addstr("path cost: {:.2f}".format(node_g))
        win.refresh()

        if done:
            success = True
            break

        curses.napms(delay_ms)

    curses.endwin()
    print(maze.toString(s.openset, s.closedset, node), end='')
    print("iterations: {:<6}".format(counter))
    print("path cost: {:.2f}".format(node_g if success else math.inf))
    print("success!" if success else "could not find path to goal :(")
