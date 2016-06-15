from tulip import *
import tulipplugins

class ImportTwoMode(object):
	def __init__(self, graph, filename, entry_separator=';', row_header_mode='A', column_header_mode='B'):
		self.graph = graph
		self.filename = filename
		self.entry_separator = entry_separator
		self.row_header_mode = row_header_mode
		self.column_header_mode = column_header_mode

	def importGraph(self):
		# This method is called to import a new graph.
		# An empty graph to populate is accessible through the "graph" class attribute
		# (see documentation of class tlp.Graph).

		# The parameters provided by the user are stored in a Tulip DataSet
		# and can be accessed through the "dataSet" class attribute
		# (see documentation of class tlp.DataSet).

		# The method must return a boolean indicating if the
		# graph has been successfully imported.
		column_nodes = []
		label = self.graph.getStringProperty('viewLabel')
		mode = self.graph.getStringProperty('mode')
		color = self.graph.getColorProperty('viewColor')
		column_color = tlp.Color.Jade
		line_color = tlp.Color.Orchid
		shape = self.graph.getIntegerProperty('viewShape')
		column_shape = tlp.NodeShape.Diamond
		line_shape = tlp.NodeShape.Circle

		with open(self.filename, 'rU') as fp:
			headers	= fp.readline()
			header_fields = headers.split(self.entry_separator)
			for f in header_fields:
				if f == '':
					continue
				n = self.graph.addNode()
				label[n] = f
				mode[n] = self.column_header_mode
				color[n] = column_color
				shape[n] = column_shape
				column_nodes.append(n)
			line = fp.readline()
			while line != '':
				row_entries = line.split(self.entry_separator)
				n = self.graph.addNode()
				label[n] = row_entries[0]
				mode[n] = self.row_header_mode
				color[n] = line_color
				shape[n] = line_shape
				row_entries.pop(0)
				for i, entry in enumerate(row_entries):
					if entry != '':
						self.graph.addEdge(n, column_nodes[i])
				line = fp.readline()
		return True

def main(graph):
	path_to_file = ''
	filename = ''
	itm = ImportTwoMode(graph, path_to_file + filename, ';', 'A', 'B')
	itm.importGraph()
