import pygraphviz as PG

# sudo apt-get install graphviz
# sudo apt-get install libgraphviz-dev
# pip install pygraphviz

def visualize(node, outFilePath):

    graph = PG.AGraph(directed=True, strict=True)
    addNodes(node, graph, "0")
    graph.layout(prog='dot')
    graph.draw(outFilePath)

def addNodes(node, graph, uniqueNum):
    
    graph.add_node(uniqueNum, label=node.toStringCleaned())
    
    childNum = 0
    for child in node.children:
        uniqueChildNum = uniqueNum + "," + str(childNum)
        graph.add_node(uniqueChildNum, label=child.toStringCleaned())
        graph.add_edge(uniqueNum, uniqueChildNum)
        addNodes(child, graph, uniqueChildNum)
        childNum += 1