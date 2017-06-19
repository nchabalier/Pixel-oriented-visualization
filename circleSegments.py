# Powered by Python 2.7

from tulip import *
import math
import copy


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

    #Initialize max and min elements for color mapping
    def initMaxMinElements(self):
      for column in self.columns:
        p = self.graph.getIntegerProperty(column)
        self.maxElements.append(p.getNodeMax())
        self.minElements.append(p.getNodeMin())
        print(p.getNodeMax(), p.getNodeMin())
    
    def createAxis(self):
        centralNode = self.graph.addNode()
        self.graph['viewLayout'][centralNode] = tlp.Vec3f(0,0,0)

        for i in range(self.nbDimension):

            node = self.graph.addNode()
            posX = math.cos(2*math.pi*i/self.nbDimension)*self.nbOfNodes
            posY = math.sin(2*math.pi*i/self.nbDimension)*self.nbOfNodes
            #print(posX, " ", posY)
            self.graph['viewLayout'][node] = tlp.Vec3f(posX,posY,0)

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
      
      for c in range(len(self.columns)):
        for n in range(len(self.nodes)):
          self.createASegment(c, n)
      
    # n: is the distance to center (the n-th node)
    # c: is the number of the attribute we are drawing
    def createASegment(self, c, n):

        node = self.duplicateNode(self.nodes[n])
        
        
        angle = 2*math.pi*(c+0.5)/self.nbDimension
        minAngle = 2*math.pi*(c)/self.nbDimension
        size = 2*n * math.sin(angle-minAngle)
        h = n * math.cos(angle-minAngle)
        posX = math.cos(angle)*h
        posY = math.sin(angle)*h
        
        self.graph['viewLayout'][node] = tlp.Vec3f(posX,posY,0)
        self.graph['viewShape'][node] =  tlp.NodeShape.Square  
        self.graph['viewSize'][node] = tlp.Size(size,1,0)
        self.graph['viewRotation'][node] = angle + math.pi/2
        #self.graph['viewColor'][node] = tlp.Color(distance%255,distance%255,distance%255)
        value = self.graph[self.columns[c]][self.nodes[n]]
        #if attribute == 6:
        #  print(value)
        value = int((float(value - self.minElements[c])/(self.maxElements[c]-self.minElements[c]))*255)
        #if attribute == 6:
        #  print("NewValue",value)
        #print(value)
        self.graph['viewColor'][node] = tlp.Color(value,value,value)
        
            



def main(graph): 
    
    graph.delEdges(graph.getEdges())
    circleSegments = CircleSegment(graph)
    #graph.delNodes(graph.getNodes())
    columns = ("Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9", "Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9")
    #columns = ("Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9")
    circleSegments.createAllCircleSegments(columns)
    
        

