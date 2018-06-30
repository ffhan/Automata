"""
Defines all visual operations, such as producing a graph.
"""
import networkx as nx
import matplotlib.pyplot as plt

def save_graph(automaton, name = 'plot.png'):
    graph = nx.MultiDiGraph()
    w_spacing = 600
    h_spacing = 300
    positions = dict()

    start_x = 50
    start_y = 200
    items = list(automaton.states.values())
    graph.add_nodes_from(items)
    current = automaton.start_state
    processed = set()
    def process(item, x, y, index):
        if item in processed:
            return
        positions[item] = (x, y + index * h_spacing)
        processed.add(item)
        total = len(item.direct_reach) // 2
        pad = len(item.direct_reach) % 2
        for single_input in automaton.inputs:
            output = item.forward(single_input)
            for index, end in enumerate(output):
                graph.add_edge(item, end, ime=single_input)
                randomizer = 50 if index % 2 else -50
                process(end, x + w_spacing, y + index * h_spacing + randomizer, (index - total))
    plt.figure(1, figsize=(40,8))
    process(current, start_x, start_y, 0)
    labels = nx.get_edge_attributes(graph,'ime')
    labels = dict(map(lambda t : (t[0][:-1], t[1]), labels.items()))
    print(labels)
    nx.draw_networkx(graph, pos=positions, with_labels=True, arrows=True, font_size=8)
    nx.draw_networkx_edge_labels(graph, pos=positions, edge_labels=labels)
    plt.savefig(name)
