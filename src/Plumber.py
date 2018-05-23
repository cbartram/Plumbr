from anytree import Node, RenderTree, DoubleStyle, LevelOrderGroupIter
import numpy as np
import os
import json
import chalk
import urllib2
import functools

class Plumber():
    def __init__(self, user, repo):
        self.repo = repo
        self.user = user
        self.root = None
        self.nodes = []

    def get_root(self):
        return self.root

    def get_nodes(self):
        return self.nodes

    def display(self):
        if self.root == None:
            raise ValueError('Your root node must be defined use build() to create a root node')
        print(chalk.yellow(self.root.name))
        for pre, fill, node in RenderTree(self.root, style=DoubleStyle):
            print("%s%s" % (chalk.blue(pre), chalk.blue(node.name)))

    def diff(self, compare_root):
        if compare_root.parent != None:
            raise ValueError('The parameter you specified is not a root node!')

        # Variables to hold number of layer and relationship differences between two trees
        layer_count = 0
        relationship_count = 0

        self.display()

        # Relationship groupings declare how each node is related to its parent  [[1], [2,3], [4, 5]] this is how tree layers and child structure is evaluated
        root_grouping = np.array([[node.parent for node in children] for children in LevelOrderGroupIter(self.root)])
        comparison_grouping = np.array([[node.parent for node in children] for children in LevelOrderGroupIter(compare_root)])

        layer_chunk = []
        comparison_chunk = []

        # Count the nodes at each layer of the tree
        for node in root_grouping:
            layer_chunk.append(len(node))

        for node in comparison_grouping:
            comparison_chunk.append(len(node))

        # Create numpy arrays out of the lists
        layer_chunk = np.array(layer_chunk)
        comparison_chunk = np.array(comparison_chunk)


        # Pad shorter array with blank values todo check for equal chunking
        if len(layer_chunk) > len(comparison_chunk):
            comparison_chunk = np.pad(comparison_chunk, (0, len(layer_chunk) - len(comparison_chunk)), 'constant')
        else:
            layer_chunk = np.pad(layer_chunk, (0, len(comparison_chunk) - len(layer_chunk)), 'constant')

        print layer_chunk
        print comparison_chunk

        # Compute difference between serialized arrays (just use layer chunk bc they are the same length)
        layer_count = functools.reduce(lambda a, b: a + b, [abs(a_i - b_i) for a_i, b_i in zip(layer_chunk, comparison_chunk)])
        percent = (functools.reduce(lambda a,b: a + b, layer_chunk) / layer_count) * 100

        return layer_count, percent

    def build(self):
        # TODO Bad....refactor this
        GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
        GITHUB_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

        # Get first commit SHA Hash
        commit_req = urllib2.urlopen(
            "https://api.github.com/repos/" + self.user + "/" + self.repo + "/commits?client_id=" + GITHUB_CLIENT_ID + "&client_secret=" + GITHUB_SECRET).read()

        commit_hash = json.loads(commit_req)[0]['commit']['tree']['sha']

        # Find the latest commit hash in order to get the tree
        url = "https://api.github.com/repos/" + self.user + "/" + self.repo + "/git/trees/" + commit_hash + "?client_id=" + GITHUB_CLIENT_ID + "&client_secret=" + GITHUB_SECRET + "&recursive=1"

        # Req for github tree structure
        tree_req = urllib2.urlopen(url).read()

        tree = json.loads(tree_req)['tree']

        self.root = Node(self.repo, parent=None)
        self.nodes = build_tree(self.root, tree)

def pad(array, reference_shape, offsets):
    # Create an array of zeros with the reference shape
    result = np.zeros(reference_shape)
    # Create a list of slices from offset to offset + shape in each dimension
    insertHere = [slice(offsets[dim], offsets[dim] + array.shape[dim]) for dim in range(array.ndim)]
    # Insert the array in the result at the specified offsets
    result[insertHere] = array
    return result


'''
This method recursively builds a directory tree
'''
def build_tree(root_node, data):
    nodes = []
    for node in data:
        path = node['path']
        type = node['type']
        path = os.path.normpath(path)
        parsed_path = path.split(os.sep)

        # The file being iterated over
        file = parsed_path[len(parsed_path) - 1]

        if len(parsed_path) == 1:
            # It is a child of the root node
            if 'size' not in node:
                nodes.append(Node(file, parent=root_node, id=len(nodes), type=type, url=node['url']))
            else:
                nodes.append(Node(file, parent=root_node, id=len(nodes), type=type, url=node['url'], size=node['size']))
        else:
            parent_dir_name = parsed_path[len(parsed_path) - 2]
            # Get the correct parent node from the list of nodes
            for n in nodes:
                # todo bug if the same file name occurs more than once in a repo
                if n.name == parent_dir_name:
                    if 'size' not in node:
                        nodes.append(Node(file, parent=n, id=len(nodes), type=type, url=node['url']))
                    else:
                        nodes.append(Node(file, parent=n, id=len(nodes), type=type, size=node['size'], url=node['url']))
    return nodes