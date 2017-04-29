"""
This contains the definition
"""

class graph():
    """
    A class containing nodes
    """

    def load_graph(self, filename):
        """
        Loads a graph.
        """
        raise NotImplementedError()

    def save_graph(self, filename):
        """
        Saves a text based representation of the current graph
        """
        raise NotImplementedError()

    def add_node(self, node):
        self.nodes.append(node)
