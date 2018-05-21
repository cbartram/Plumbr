from anytree import Node, RenderTree, DoubleStyle
import os
import json
import chalk
import urllib2

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
        # TODO Find the difference between the self.root and compare_root
        return True

    def build(self):
        GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID") or '039cfdf30c82f07aa5de'
        GITHUB_SECRET = os.getenv("GITHUB_CLIENT_SECRET") or 'a941deef5acac3f2496326208442498e8a83b828'

        # Get first commit SHA Hash
        commit_req = urllib2.urlopen(
            "https://api.github.com/repos/" + self.user + "/" + self.repo + "/commits?client_id=" + GITHUB_CLIENT_ID + "&client_secret=" + GITHUB_SECRET).read()

        commit_hash = json.loads(commit_req)[0]['commit']['tree']['sha']

        # Find the latest commit hash in order to get the tree
        url = "https://api.github.com/repos/" + self.user + "/" + self.repo + "/git/trees/" + commit_hash + "?client_id=" + GITHUB_CLIENT_ID + "&client_secret=" + GITHUB_SECRET + "&recursive=1"

        # Req for github tree structure
        tree_req = urllib2.urlopen(url).read()

        tree = json.loads(tree_req)['tree']

        print(chalk.green('Creating Tree -> ' + self.repo))
        self.root = Node(self.repo, parent=None)
        self.nodes = build_tree(self.root, tree)

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

        # Add the root files nodes
        if "/" not in node['path'] and type == "blob":
            nodes.append(Node(node['path'], parent=root_node, type=type, size=node['size'], url=node['url']))

        # Add the root directory nodes
        if "/" not in node['path'] and type == "tree":
            nodes.append(Node(node['path'], parent=root_node, type=type, url=node['url']))
        # If there are nested directories
        if len(parsed_path) > 1:
            file = parsed_path[len(parsed_path) - 1]
            parent_dir_name = parsed_path[len(parsed_path) - 2]

            index = 0
            # Get the correct parent node from the list of nodes
            for n in nodes:
                if n.name == parent_dir_name:
                    if 'size' not in node:
                        nodes.append(Node(file, parent=n, type=type, url=node['url']))
                    else:
                        nodes.append(Node(file, parent=n, type=type, size=node['size'], url=node['url']))
                index += 1
    return nodes