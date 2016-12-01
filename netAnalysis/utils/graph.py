import json

class Graph:
    """Graph class with nodes and edges"""

    def __init__(self, nodes={}, edges=[]):
        """

        :param nodes: dict of node names, each is a dict of its regulators
                      nodes['G100'] = {'G20': 0.3, 'G43': 0.2, ...}
        :param edges: list of {'source': source, 'target':target, 'weight':value}
        """
        self.nodes = nodes
        self.links = edges

    def addNode(self, name):
        self.nodes[name] = {}

    def addLink(self, source, target, value=0):
        self.links.append({'source': source, 'target':target, 'weight':value})
        if (source not in self.nodes):
            self.addNode(source)
        if (target not in self.nodes):
            self.addNode(target)

        self.nodes[target][source] =  value

    def getLinks(self):
        return self.links

    def getNodes(self):
        return list(self.nodes.keys())

    def getNodeRegulators(self, node):
        if node in self.nodes:
            return self.nodes[node].keys()
        else:
            return []

# ----------------------------------------------------------

def mainTest():
    graph = Graph()
    graph.addLink(1,3,4)
    graph.addLink(1,4,4)
    graph.addLink(4,5,.3)
    graph.addLink(4,1,4)
    print(json.dumps(graph.getLinks()))
    print(graph.getNodeRegulators(1))
    print(graph.getNodes())


if __name__ == "__main__":
    mainTest()
