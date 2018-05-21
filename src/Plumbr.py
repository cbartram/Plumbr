from flask import Flask
from anytree import Node, RenderTree
from flask import jsonify
import os
import json
import chalk
import urllib2

global root_one
global root_two

app = Flask(__name__)

def print_tree(root):
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))

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
            for node in nodes:
                if node.name == parent_dir_name:
                    nodes.append(Node(file, parent=node))
                index += 1

'''
 Renders a basic test route using dummy loaded json data
'''
@app.route('/test')
def test():
    with open('data.json') as f:
        data = json.load(f)
        root_node = Node('nanoleaf-layout', parent=None)
        build_tree(root_node, data)

        print_tree(root_node)

        return jsonify(data)

'''
Renders the index page alerting users to use different routes
'''
@app.route('/')
def index():
  return jsonify({
            'error': True,
            'message': 'You must specify the correct path! try /github_username/your_repository_name'
        })



@app.route('/display/<int:root>')
def display(root):
    if root == 1:
        return print_tree(root_one)
    else:
        return print_tree(root_two)

'''
Handles parsing the directory tree structure for the first dir
'''
@app.route('/build/<int:root>/<user>/<repo>')
def dir_tree(root, user, repo):
    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

    # Get first commit SHA Hash
    commit_req = urllib2.urlopen("https://api.github.com/repos/" + user + "/" + repo + "/commits?client_id=" + GITHUB_CLIENT_ID + "&client_secret=" + GITHUB_SECRET).read()

    commit_hash = json.loads(commit_req)[0]['commit']['tree']['sha']

    # Find the latest commit hash in order to get the tree
    url = "https://api.github.com/repos/" + user + "/" + repo + "/git/trees/" + commit_hash + "?client_id=" + GITHUB_CLIENT_ID + "&client_secret=" + GITHUB_SECRET + "&recursive=1"

    # Req for github tree structure
    tree_req = urllib2.urlopen(url).read()

    tree = json.loads(tree_req)['tree']

    if root == 1:
        print(chalk.green('Creating Tree One ->' + repo))
        root_one = Node(repo, parent=None)
        build_tree(root_one, tree)
    else:
        print(chalk.green('Creating Tree Two ->' + repo))
        root_two = Node(repo, parent=None)
        build_tree(root_two, tree)

    return jsonify(tree)

if __name__ == '__main__':
    app.run()
