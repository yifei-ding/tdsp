import sys


class State(object):
    def __init__(self, node, timestep, g, parent, goal_vertex):
        """
        g(x) is the actual distance from start to current vertex
        h(x) is the estimated distance from current to end vertex
        f = g + h
        """
        self.node = node
        self.timestep = timestep
        self.g = g
        self.h = 0
        self.parent = parent
        self.goal_vertex = goal_vertex

    @classmethod
    def from_parent(cls, node, parent):
        return cls(node=node, timestep=None, g=sys.maxsize, parent=parent, goal_vertex=parent.get_goal_vertex())

    def get_goal_vertex(self):
        return self.goal_vertex

    def set_timestep(self, timestep):
        self.timestep = timestep

    def set_h(self):
        self.h = self.distance(self.node, self.get_goal_vertex())

    def get_h(self):
        return self.h

    def get_f(self):
        return self.g + self.h

    def set_parent(self, parent):
        self.parent = parent

    def get_node(self):
        return self.node

    def get_timestep(self):
        return self.timestep

    def get_g(self):
        return self.g

    def set_g(self, g):
        self.g = g

    def extract_path(self):
        state = self
        path2 = [state]
        while state.parent is not None:
            state = state.parent
            path2.append(state)
        return path2

    def __lt__(self, other):
        return self.get_f < other.get_f

    def __gt__(self, other):
        return self.get_f > other.get_f

    def __eq__(self, other):
        # and self.timestep == other.timestep and self.cost == other.cost
        return self.node == other.node and self.timestep == other.timestep

    def __repr__(self):
        return "node={0}, timestep={1}, cost={2}".format(self.node, self.timestep, self.g)

    @staticmethod
    def distance(self, node, end_vertex):
        # TODO
        return 0

    def is_goal(self):
        return self.node == self.goal_vertex
