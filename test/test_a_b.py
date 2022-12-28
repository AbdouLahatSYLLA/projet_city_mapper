import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import write_dot

with open('network_walk.csv', 'r') as f:

    next(f)
    G = nx.Graph()
    for line in f:
        items = line.rstrip("\n").split(";")
        for item in items:

            #replace ' with '', for strings in postgreSQL
            item = item.replace("'", "''")
            if item == items[0]:
                G.add_node(int(item))
            if item == items[1] :
                G.add_node(int(item))
                G.add_edge(items[0], items[1], weight = items[3])

#print(list(nx.connected_components(G)))
pos = nx.nx_agraph.graphviz_layout(G)
nx.draw(G, pos=pos)
write_dot(G, 'file.dot')
