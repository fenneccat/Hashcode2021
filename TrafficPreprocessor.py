#!/usr/bin/env python
# coding: utf-8

# In[1]:


from collections import deque


# In[2]:


class Graph:
    def __init__(self, num_intersection, num_street):
        self.num_intersections = num_intersection
        self.num_street = num_street
        self.graph = dict()
        self.incoming_streets = dict()
        self.streets_length = dict()
    
    def add_street(self, begin, end, length, street_index):
        self.graph.setdefault(begin, []).append((street_index, end))
        self.incoming_streets.setdefault(end, []).append((street_index, begin))
        self.streets_length[(begin, end)] = length
        self.streets_length[street_index] = length
    
    def get_incoming_streets(self, intersection):
        if intersection in self.incoming_streets:
            return [x[0] for x in self.incoming_streets[intersection]]
        else: return []
    
    def get_outgoing_streets(self, intersection):
        if intersection in self.graph:
            return [x[0] for x in self.graph[intersection]]
        else: return []
        
    def get_outgoing_intersections(self, intersection):
        if intersection in self.graph:
            return [x[1] for x in self.graph[intersection]]
        else: return []
        
    def get_intersections(self):
        return list(range(self.num_intersections))

    def get_dict_intersection_to_streets(self):
        intersections = self.get_intersections()
        ret_dict = {}
        for intersection in intersections:
            ret_dict[intersection] = self.get_incoming_streets(intersection)
        return ret_dict


# In[3]:


def readTraffic(path):
    f = open(path, 'r')
    D, I, S, V, F = map(int, f.readline().split())

    street2idx = dict()
    idx2street = dict()

    street_map = Graph(I, S)

    B = E = L = 0
    for i in range(S):
        B, E, street_name, L = f.readline().split()
        B = int(B)
        E = int(E)
        L = int(L)
        street_map.add_street(B, E, L, i)
        street2idx[street_name] = i
        idx2street[i] = street_name

    cars_path = dict()
    for i in range(V):
        path_len, path = f.readline().split(" ", 1)
        for street in path.split():
            cars_path.setdefault(i, deque([])).append(street2idx[street])
    
    return D, I, S, V, F, street2idx, idx2street, cars_path, street_map

