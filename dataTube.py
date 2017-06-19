# Powered by Python 2.7

from tulip import *
import math
import copy


class Trapezoid():
  
  def __init__(self, graph, coord, rotation, size, triangleWidth):
    self.graph = graph
    self.coord = coord
    self.rotation = rotation
    self.size = size  
    self.triangleWidth = self.size.getH()*triangleWidth
    
    self.drawTrapezoid()
  
  def drawTrapezoid(self):
    self.rectangleNode = self.graph.addNode()
    self.graph['viewLayout'][self.rectangleNode] = self.coord
    self.graph['viewShape'][self.rectangleNode] = tlp.NodeShape.Square
    self.graph['viewSize'][self.rectangleNode] = self.size
    self.graph['viewRotation'][self.rectangleNode] = self.rotation
  
    #Height of the rectangle / 2
    dist = self.size.getH()/2
    #Vector from the center of the rectangle to the 
    vec = tlp.Coord(dist*math.cos(self.rotation+math.pi/2), dist*math.sin(self.rotation+math.pi/2), 0)
    
    self.triangleNode1 = self.graph.addNode()
    self.graph['viewLayout'][self.triangleNode1] = self.coord + vec
    self.graph['viewShape'][self.triangleNode1] = tlp.NodeShape.Triangle
    self.graph['viewSize'][self.triangleNode1] = tlp.Size(self.triangleWidth,self.size.getW(),0)
    self.graph['viewRotation'][self.triangleNode1] = self.rotation+math.pi/2
    
    self.triangleNode2 = self.graph.addNode()
    self.graph['viewLayout'][self.triangleNode2] = self.coord - vec
    self.graph['viewShape'][self.triangleNode2] = tlp.NodeShape.Triangle
    self.graph['viewSize'][self.triangleNode2] = tlp.Size(self.triangleWidth,self.size.getW(),0)
    self.graph['viewRotation'][self.triangleNode2] = self.rotation+math.pi/2
    
  def color(self, color):
    self.graph['viewColor'][self.rectangleNode] = color
    self.graph['viewColor'][self.triangleNode1] = color
    self.graph['viewColor'][self.triangleNode2] = color
    

class CircleSegment:
    def __init__(self, graph):
        self.graph = graph.addSubGraph("Data Tube")
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
    def createAllCircleSegments(self, columns, trapezoidWidth):
      self.columns = columns
      self.nbDimension = len(columns)
      
      
      #self.createAxis()
      self.initMaxMinElements()
      
      cmpTest = 0
      for c in range(len(self.columns)):
        if True:#cmpTest%2 == 0:
          self.currentPos = 2
          for n in range(len(self.nodes)): #
            #for _ in range(self.currentPos):
            self.createASegment(c, n,trapezoidWidth)
            self.currentPos+=self.currentPos*trapezoidWidth
        cmpTest+=1
      
    # n: is the distance to center (the n-th node)
    # c: is the number of the attribute we are drawing
    def createASegment(self, c, n, trapezoidWidth):

        angle = 2*math.pi*(c+0.5)/self.nbDimension
        minAngle = 2*math.pi*(c)/self.nbDimension
       
        tempX = math.cos(angle)*self.currentPos
        tempY = math.sin(angle)*self.currentPos
        #The weight of rectangle
        height = 2.0*math.sqrt(tempX*tempX + tempY*tempY)*math.tan(angle-minAngle)
        
        #Position to place the rectangle
        posX = math.cos(angle)*self.currentPos*(1.0+trapezoidWidth/2.0)
        posY = math.sin(angle)*self.currentPos*(1.0+trapezoidWidth/2.0)
        coord = tlp.Coord(posX,posY,0)
        size = tlp.Size(self.currentPos*trapezoidWidth,height,0)
        
        
        
        trapezoid = Trapezoid(self.graph, coord, angle, size,trapezoidWidth)
        
        
        
        value = self.graph[self.columns[c]][self.nodes[n]]

        value = int((float(value - self.minElements[c])/(self.maxElements[c]-self.minElements[c]))*255)

        trapezoid.color(tlp.Color(value,value,value))
        
            



def main(graph): 
    
    graph.delEdges(graph.getEdges())
    circleSegments = CircleSegment(graph)
    #graph.delNodes(graph.getNodes())
    #columns = ("Column_0", "Column_1", "Column_2", "Column_3")
    columns = ("Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9","Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9", "Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9","Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9")
    circleSegments.createAllCircleSegments(columns, 0.005)
