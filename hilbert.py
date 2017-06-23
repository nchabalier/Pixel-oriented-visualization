# -*- coding:utf-8 -*-
 
from tulip import *
import math
 
class Hilbert(object):
	'''
	embeds nodes in a graph along a Hilbert curve
	'''
	def __init__(self, graph):
		super(Hilbert, self).__init__()
		self.graph = graph
		self.direction_vector = tlp.Vec3f(1, 0, 0)
		self.current_coord = tlp.Coord(0,0,0)
		self.sequence = self.setAxiom()
 
	def setAxiom(self):
		return ['L']
 
	def rewrite(self, letter):
		'''
		implements the rewrite rules
		return a list of symbols L, R, F, +, -
		'''
		if (letter == 'L'):
			return list(['-','R','F','+','L','F','L','+','F','R','-'])
		if (letter == 'R'):
			return list(['+','L','F','-','R','F','R','-','F','L','+'])
		else:
			return list(letter)
 
	def iteration_order(self, curve_length):
		'''
		computes to order up to which the sequence must be
		rewritten in order to have enough points on the curve
		to fit all nodes in the graph
		'''
		rep = 1
		n = 4
		while (n < curve_length):
			rep = rep + 1
			n = n * 4
		return rep + 1
 
	def flatten(self, nested_list):
		return [x for sublist in nested_list for x in sublist]
 
	def L_expression(self, n):
		'''
		applies the rewrite rule to self.sequence
		maps rewrite rules on each letter
		concatenates the result into a single list
		'''
		while (n > 1):
			n = n-1
			newSequence = []
			for letter in self.sequence:
				newSequence = newSequence + self.rewrite(letter)
			self.sequence = newSequence
 
	def rotate_dir_vector(self, direction):
		'''
		applies a rotation to self.direction_vector
		where direction is an angle
		uses the usual 2D rotation matrix
		NB: Vec3f implements dotProduct
		'''
		x = self.direction_vector.getX()
		y = self.direction_vector.getY()
		newX = x * math.cos(direction) - y * math.sin(direction)
		newY = x * math.sin(direction) + y * math.cos(direction)
		self.direction_vector = tlp.Vec3f(newX, newY, 0)
 
	def process_sequence(self):
		'''
		uses the sequence and maps nodes to coordonates inthe 2D plane
		each letter in the sequence correspond to either
		- mapping coordinaletes to a node (L, R)
		- going forward (F) according to the directional vector
		- rotating the directional vector (+, -)
		'''
		id = 0
		for letter in self.sequence:
			if id < self.graph.numberOfNodes():
				if (letter == 'L' or letter == 'R'):
					node = list(self.graph.getNodes())[id]
					self.graph.getLayoutProperty("viewLayout")[node] = self.current_coord
					id = id + 1
				if (letter == 'F'):
					self.current_coord = self.current_coord + 2 * self.direction_vector
				if (letter == '+'):
					self.rotate_dir_vector(math.pi / 2)
				if (letter == '-'):
					self.rotate_dir_vector(math.pi / -2)
 
def main(graph):
	hilb = Hilbert(graph)
	n = hilb.iteration_order(graph.numberOfNodes())
	hilb.L_expression(n)
	print (len(hilb.sequence))
	hilb.process_sequence()
	updateVisualization()
