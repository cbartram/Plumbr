from flask import Flask
from anytree import Node, RenderTree
from flask import jsonify
from pprint import pprint
import os
import json
import chalk
import urllib2

app = Flask(__name__)

def print_tree(root):
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))

'''
This method recursively builds a directory tree
'''
def build_tree(root_node, data):
    nodes = []
    print(chalk.green("Building Directory Tree.."))
    for node in data:
        path = node['path']
        type = node['type']
        path = os.path.normpath(path)
        parsed_path = path.split(os.sep)

        # Add the root files nodes
        if "/" not in node['path'] and type == "blob":
            print(chalk.blue('Parsing Root File -> ' + node['path']))
            nodes.append(Node(node['path'], parent=root_node))

        # Add the root directory nodes
        if "/" not in node['path'] and type == "tree":
            nodes.append(Node(node['path'], parent=root_node))

        # If there are nested directories
        if len(parsed_path) > 1:
            file = parsed_path[len(parsed_path) - 1]
            parent_dir_name = parsed_path[len(parsed_path) - 2]

            index = 0
            # Get the correct parent node from the list of nodes
            for n in nodes:
                if n.name == parent_dir_name:
                    nodes.append(Node(file, parent=n))
                index += 1




@app.route('/test')
def test():
    with open('data.json') as f:
        data = json.load(f)
        root_node = Node('nanoleaf-layout', parent=None)
        build_tree(root_node, data)

        print_tree(root_node)

        return jsonify(data)

@app.route('/')
def index():
    # https://api.github.com/repos/cbartram/nanoleaf-layout/git/trees/7ced698dd814b1575508a1a563332ca8b2ed342a?client_id=039cfdf30c82f07aa5de&client_secret=a941deef5acac3f2496326208442498e8a83b828&recursive=1

    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

    # Get first commit SHA Hash
    commit_req = urllib2.urlopen("https://api.github.com/repos/cbartram/nanoleaf-layout/commits?client_id=" + GITHUB_CLIENT_ID + "&client_secret=" + GITHUB_SECRET).read()

    commit_hash = json.loads(commit_req)[0]['commit']['tree']['sha']

    # Find the latest commit hash in order to get the tree
    # TODO Something is weird here...
    a = "https://api.github.com/repos/cbartram/nanoleaf-layout/git/trees/" + commit_hash + "?client_id=" + GITHUB_CLIENT_ID + "&client_secret=" + GITHUB_SECRET + "&recursive=1"
    b = "https://api.github.com/repos/cbartram/nanoleaf-layout/git/trees/7ced698dd814b1575508a1a563332ca8b2ed342a?client_id=039cfdf30c82f07aa5de&client_secret=a941deef5acac3f2496326208442498e8a83b828&recursive=1"
    
    # Req for github tree structure
    tree_req = urllib2.urlopen(b).read()

    tree = json.loads(tree_req)['tree']
    root_node = Node('nanoleaf-layout', parent=None)

    build_tree(root_node, tree)

    print_tree(root_node)

    return jsonify(tree)

if __name__ == '__main__':
    app.run()
