from tulip import *
import tulipplugins
import math
import copy

class DataTubePlugin(tlp.Algorithm):
        def __init__(self, context):
                tlp.Algorithm.__init__(self, context)
                # you can add parameters to the plugin here through the following syntax
                # self.add<Type>Parameter("<paramName>", "<paramDoc>", "<paramDefaultValue>")
                # (see documentation of class tlp.WithParameter to see what types of parameters are supported)
                self.addFloatParameter("size","Width of each node","0.005");
                self.addNumericPropertyParameter("sorted by","Sort the node by the selected propertie","viewMetric",True,True,False)
                self.addColorScaleParameter("color scale", "The color scale used to node property value into a color")
                
                #self.addIntegerVectorPropertyParameter("c","help","inDefValue",True,True,False,"Description")
                #self.addStringCollectionParameter(

        def check(self):
                # This method is called before applying the algorithm on the input graph.
                # You can perform some precondition checks here.
                # See comments in the run method to know how to access to the input graph.

                # Must return a tuple (boolean, string). First member indicates if the algorithm can be applied
                # and the second one can be used to provide an error message
                return (True, "Ok")

        def run(self):
                # This method is the entry point of the algorithm when it is called
                # and must contain its implementation.

                # The graph on which the algorithm is applied can be accessed through
                # the "graph" class attribute (see documentation of class tlp.Graph).

                # The parameters provided by the user are stored in a Tulip DataSet
                # and can be accessed through the "dataSet" class attribute
                # (see documentation of class tlp.DataSet).
                
                properties = getNumericProperties(self.graph)
                
                
                size = self.dataSet["size"]
                sortProperty = self.dataSet["sorted by"]
                colorScale = self.dataSet["color scale"]
                
                
                self.graph.delEdges(self.graph.getEdges())
                circleSegments = CircleSegment(self.graph, sortProperty, colorScale)
                #graph.delNodes(graph.getNodes())
                #columns = ("Column_0", "Column_1", "Column_2", "Column_3")
                #columns = ("Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9","Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9", "Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9","Column_0", "Column_1", "Column_2", "Column_3", "Column_6", "Column_7", "Column_9")
                circleSegments.createAllCircleSegments(properties, size)                
                

                # The method must return a boolean indicating if the algorithm
                # has been successfully applied on the input graph.
                return True


def getNumericProperties(graph):
  numericProperties = []
  properties = graph.getObjectProperties()
  #properties = graph.getLocalObjectProperties()
  for p in properties:
    if isinstance(p, tlp.NumericProperty):
      if p.getName() not in ["viewBorderWidth", "viewFontSizeview","LabelBorderWidth", "viewLabelPositionview","MetricviewRotation", "viewShape", "viewSrcAnchorShape", "viewTgtAnchorShape"
      ,"viewFontSize","viewLabelBorderWidth","viewLabelPosition","viewRotation"]:
        numericProperties.append(p)
  return numericProperties


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
    def __init__(self, graph, sortProperty, colorScale):
        self.graph = graph.addSubGraph("Data Tube")
        self.sortProperty = sortProperty
        self.colorScale = colorScale
        
        self.nbOfNodes = graph.numberOfNodes()
        self.nodes = []
        
        self.nodes = list(graph.getNodes())
        self.nodes.sort(key=lambda x: sortProperty[x], reverse=True)
        self.maxElements = []
        self.minElements = []
        self.currentPos = 1.0

    #Initialize max and min elements for color mapping
    def initMaxMinElements(self):
      for p in self.properties:
        self.maxElements.append(p.getNodeMax())
        self.minElements.append(p.getNodeMin())
       
    
    def createAxis(self):
        centralNode = self.graph.addNode()
        self.graph['viewLayout'][centralNode] = tlp.Vec3f(0,0,10)

        for i in range(self.nbDimension):

            node = self.graph.addNode()
            posX = math.cos(2*math.pi*i/self.nbDimension)*self.nbOfNodes
            posY = math.sin(2*math.pi*i/self.nbDimension)*self.nbOfNodes
            
            self.graph['viewLayout'][node] = tlp.Vec3f(posX,posY,10)

            edge = self.graph.addEdge(centralNode, node)
    
    def duplicateNode(self, node):
      newNode = self.graph.addNode()
      for p in self.properties:
        p[newNode] = p[node]
      return newNode


    #Create all the complete circle segment graph with attributes given
    def createAllCircleSegments(self, properties, trapezoidWidth):
      self.properties = properties
      self.nbDimension = len(properties)
      
      
      #self.createAxis()
      self.initMaxMinElements()
      
      cmpTest = 0
      for c in range(len(self.properties)):
        if True:#cmpTest%2 == 0:
          self.currentPos = 2
          for n in range(len(self.nodes)): 
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
        
        
        
        value = self.properties[c][self.nodes[n]]

        #value = int((float(value - self.minElements[c])/(self.maxElements[c]-self.minElements[c]))*255)
        if self.maxElements[c] != self.minElements[c]:
          value = float(value - self.minElements[c])/(self.maxElements[c]-self.minElements[c])
        else:
          value = 0.0
          
        color = self.getColorAtPos(value)

        trapezoid.color(color)
        
            
    #Returns the color for a given position in the color scale. This method computes the color associated to a specific position in the color scale and returns it. 
    def getColorAtPos(self, pos):
    
      theColor = None
      minDist = 1.0
      
      for value, color in self.colorScale.iteritems():
        newDist = abs(pos-value)
        
        if newDist < minDist:
          theColor = color
          minDist = newDist
      
      return theColor

# The line below does the magic to register the plugin to the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPluginOfGroup("DataTubePlugin", "Data Tube", "Nicolas Chabalier", "18/06/2017", "infos", "1.0", "Python")
