from flask import Flask
from anytree import Node, RenderTree
from flask import jsonify
from string import Template
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
def build_tree(base_url, root_node, data):
    for file in data:
        n = Node(file['name'], parent=root_node)
        if file['type'] == "dir":
            print(chalk.blue("Reading Root Directory -> " +  base_url + file['name']))
            content = urllib2.urlopen(base_url + file['name']).read()
            for c in json.loads(content):
                Node(c['name'], parent=n)
                print(chalk.green('Reading Sub Directory -> ' + base_url + file['name'] + "/" + c['name']))
                #build_tree(base_url + file['name'] + "/" + c['name'], Node(c['name'], parent=Node(file['name'])), json.loads(content))

@app.route('/')
def hello_world():
    base_url = "https://api.github.com/repos/cbartram/nanoleaf-layout/contents/"

    # Get root from Github
    contents = urllib2.urlopen(base_url).read()

    # Parse JSON Data
    data = json.loads(contents)

    root_node = Node('nanoleaf-layout', parent=None)
    build_tree(base_url, root_node, data)

    print_tree(root_node)


    return jsonify(contents)


if __name__ == '__main__':
    app.run()
