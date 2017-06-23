from tulip import *
import tulipplugins
import math
import copy

class CircleSegmentsPlugin(tlp.Algorithm):
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
                for property in properties:
                #  print self.graph[property]
                  print property
                
                size = self.dataSet["size"]
                sortProperty = self.dataSet["sorted by"]
                colorScale = self.dataSet["color scale"]
                #colorScale.getColorAtPos(0.5)
                print("Color scale: ", type(colorScale))
                for key, value in colorScale.iteritems():
                  print(key, value)
                
                self.graph.delEdges(self.graph.getEdges())
                circleSegments = CircleSegment(self.graph, sortProperty, colorScale)
                
                circleSegments.createAllCircleSegments(properties)                
                

                # The method must return a boolean indicating if the algorithm
                # has been successfully applied on the input graph.
                return True


def getNumericProperties(graph):
  numericProperties = []
  properties = graph.getObjectProperties()
  
  for p in properties:
    if isinstance(p, tlp.NumericProperty):
      if p.getName() not in ["viewBorderWidth", "viewFontSizeview","LabelBorderWidth", "viewLabelPositionview","MetricviewRotation", "viewShape", "viewSrcAnchorShape", "viewTgtAnchorShape"
      ,"viewFontSize","viewLabelBorderWidth","viewLabelPosition","viewRotation"]:
        numericProperties.append(p)
  return numericProperties


class CircleSegment:
    def __init__(self, graph, sortProperty, colorScale):
        self.graph = graph.addSubGraph("CircleSegments")
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
      for p in self.columns:
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
        column[newNode] = column[node]
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
        
        value = self.columns[c][self.nodes[n]]


        #value = int((float(value - self.minElements[c])/(self.maxElements[c]-self.minElements[c]))*255)
        if self.maxElements[c] != self.minElements[c]:
          value = float(value - self.minElements[c])/(self.maxElements[c]-self.minElements[c])
        else:
          value = 0.0
          
        color = self.getColorAtPos(value)
        
        self.graph['viewColor'][node] = color
        
    #Returns the color for a given position in the color scale. This method computes the color associated to a specific position in the color scale and returns it. 
    def getColorAtPos(self, pos):
    
      theColor = None
      minDist = 1.0
      
      for value, color in self.colorScale.iteritems():
        newDist = abs(pos-value)
        #print(newDist)
        if newDist < minDist:
          theColor = color
          minDist = newDist
      
      return theColor
# The line below does the magic to register the plugin to the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPluginOfGroup("CircleSegmentsPlugin", "Circle Segments", "Nicolas Chabalier", "18/06/2017", "infos", "1.0", "Python")
