# Powered by Python 2.7

# To cancel the modifications performed by the script
# on the current graph, click on the undo button.

# Some useful keyboards shortcuts : 
#   * Ctrl + D : comment selected lines.
#   * Ctrl + Shift + D  : uncomment selected lines.
#   * Ctrl + I : indent selected lines.
#   * Ctrl + Shift + I  : unindent selected lines.
#   * Ctrl + Return  : run script.
#   * Ctrl + F  : find selected text.
#   * Ctrl + R  : replace selected text.
#   * Ctrl + Space  : show auto-completion dialog.

from tulip import *
import math
import copy

# the updateVisualization(centerViews = True) function can be called
# during script execution to update the opened views

# the pauseScript() function can be called to pause the script execution.
# To resume the script execution, you will have to click on the "Run script " button.

# the runGraphScript(scriptFile, graph) function can be called to launch another edited script on a tlp.Graph object.
# The scriptFile parameter defines the script name to call (in the form [a-zA-Z0-9_]+.py)

# the main(graph) function must be defined 
# to run the script on the current graph

class Trapezoid():
  
  def __init__(self, graph, coord, rotation, size):
    self.graph = graph
    self.coord = coord
    self.rotation = rotation
    self.size = size  
    
    self.drawTrapezoid()
  
  def drawTrapezoid(self):
    self.rectangleNode = graph.addNode()
    graph['viewLayout'][self.rectangleNode] = self.coord
    graph['viewShape'][self.rectangleNode] = tlp.NodeShape.Square
    graph['viewSize'][self.rectangleNode] = self.size
    graph['viewRotation'][self.rectangleNode] = self.rotation
  
    #Height of the rectangle / 2
    dist = self.size.getH()/2
    #Vector from the center of the rectangle to the 
    vec = tlp.Coord(dist*math.cos(self.rotation+math.pi/2), dist*math.sin(self.rotation+math.pi/2), 0)
    
    self.triangleNode1 = graph.addNode()
    graph['viewLayout'][self.triangleNode1] = self.coord + vec
    graph['viewShape'][self.triangleNode1] = tlp.NodeShape.Triangle
    graph['viewSize'][self.triangleNode1] = tlp.Size(self.size.getH()/2,self.size.getW(),0)
    graph['viewRotation'][self.triangleNode1] = self.rotation+math.pi/2
    
    self.triangleNode2 = graph.addNode()
    graph['viewLayout'][self.triangleNode2] = self.coord - vec
    graph['viewShape'][self.triangleNode2] = tlp.NodeShape.Triangle
    graph['viewSize'][self.triangleNode2] = tlp.Size(self.size.getH()/2,self.size.getW(),0)
    graph['viewRotation'][self.triangleNode2] = self.rotation+math.pi/2
    
  def color(self, color):
    self.graph['viewColor'][self.rectangleNode] = color
    self.graph['viewColor'][self.triangleNode1] = color
    self.graph['viewColor'][self.triangleNode2] = color
    

class CircleSegment:
    def __init__(self, graph):
        self.graph = graph.addSubGraph("CircleSegments")
        #self.nbDimension = 7 #TODO: nbDimension = nb of attributes
        self.nbOfNodes = graph.numberOfNodes()
        self.nodes = []
        #self.columns = []
        self.nodes = list(graph.getNodes())
        self.nodes.sort(key=lambda x: self.graph['Column_0'][x], reverse=True)
        self.maxElements = []
        self.minElements = []
        self.currentPos = 1

    #Initialize max and min elements for color mapping
    def initMaxMinElements(self):
      for column in self.columns:
        p = self.graph.getIntegerProperty(column)
        self.maxElements.append(p.getNodeMax())
        self.minElements.append(p.getNodeMin())
        print(p.getNodeMax(), p.getNodeMin())
    
    def createAxis(self):
        centralNode = self.graph.addNode()
        self.graph['viewLayout'][centralNode] = tlp.Vec3f(0,0,10)

        for i in range(self.nbDimension):

            node = self.graph.addNode()
            posX = math.cos(2*math.pi*i/self.nbDimension)*self.nbOfNodes
            posY = math.sin(2*math.pi*i/self.nbDimension)*self.nbOfNodes
            #print(posX, " ", posY)
            self.graph['viewLayout'][node] = tlp.Vec3f(posX,posY,10)

            edge = self.graph.addEdge(centralNode, node)
    
    def duplicateNode(self, node):
      newNode = self.graph.addNode()
      for column in self.columns:
        self.graph[column][newNode] = self.graph[column][node]
      return newNode


    #Create all the complete circle segment graph with attributes given
    def createAllCircleSegments(self, columns):
      self.columns = columns
      self.nbDimension = len(columns)
      
      
      self.createAxis()
      self.initMaxMinElements()
      
      cmpTest = 0
      for c in range(len(self.columns)):
        if True:#cmpTest%2 == 0:
          self.currentPos = 2
          for n in range(50):#range(len(self.nodes)): #
            #for _ in range(self.currentPos):
            self.createASegment(c, n)
            self.currentPos+=self.currentPos/2
        cmpTest+=1
      
    # n: is the distance to center (the n-th node)
    # c: is the number of the attribute we are drawing
    def createASegment(self, c, n):

        #node = self.duplicateNode(self.nodes[n])
        
        
        angle = 2*math.pi*(c+0.5)/self.nbDimension
        minAngle = 2*math.pi*(c)/self.nbDimension
        #height = 2*self.currentPos * math.sin(angle-minAngle)
        #h = self.currentPos * math.cos(angle-minAngle)
        height = self.currentPos * math.sin(angle-minAngle)*2
        #h2 = self.currentPos*(3/2) * math.cos(angle-minAngle)
        posX = math.cos(angle)*self.currentPos*(1.25)
        posY = math.sin(angle)*self.currentPos*(1.25)
        coord = tlp.Coord(posX,posY,0)
        size = tlp.Size(self.currentPos/2,height,0)
        
        
        #triangleSize = 
        
        trapezoid = Trapezoid(self.graph, coord, angle, size)
        
        #self.graph['viewLayout'][node] = tlp.Vec3f(posX,posY,0)
        #self.graph['viewShape'][node] =  tlp.NodeShape.Square  
        #self.graph['viewSize'][node] = tlp.Size(size,1,0)
        #self.graph['viewRotation'][node] = angle + math.pi/2
        #self.graph['viewColor'][node] = tlp.Color(distance%255,distance%255,distance%255)
        value = self.graph[self.columns[c]][self.nodes[n]]
        #if attribute == 6:
        #  print(value)
        value = int((float(value - self.minElements[c])/(self.maxElements[c]-self.minElements[c]))*255)
        #if attribute == 6:
        #  print("NewValue",value)
        #print(value)
        #self.graph['viewColor'][node] = tlp.Color(value,value,value)
        trapezoid.color(tlp.Color(value,value,value))
        
            



def main(graph): 
    
    graph.delEdges(graph.getEdges())
    circleSegments = CircleSegment(graph)
    #graph.delNodes(graph.getNodes())
    columns = ("Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9","Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9", "Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9","Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9")
    circleSegments.createAllCircleSegments(columns)
    
        

