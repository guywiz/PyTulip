from tulip import *
import tulipplugins

class ImportTwoMode(tlp.ImportModule):
	def __init__(self, context):
		tlp.ImportModule.__init__(self, context)
		# you can add parameters to the plugin here through the following syntax
		# self.add<Type>Parameter("<paramName>", "<paramDoc>", "<paramDefaultValue>")
		# (see documentation of class tlp.WithParameter to see what types of parameters are supported)
		self.addStringParameter("file::filename", \
			"File from which data is loaded. First line and first column contain headers. Other entries indicate links.", \
			"")
		self.addStringParameter("Entry separator", "Character used to separate fields.", ";")
		self.addStringParameter("Row header mode", "Mode label for row entries.", "A")
		self.addStringParameter("Column header mode", "Mode label for column entries.", "B")

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

		entry_separator = self.dataSet['Entry separator']
		filename = self.dataSet['file::filename']
		with open(filename, 'rU') as fp:
			headers	= fp.readline()
			header_fields = headers.split(entry_separator)
			col_mode = self.dataSet['Column header mode']
			for f in header_fields:
				if f == '':
					continue
				n = self.graph.addNode()
				label[n] = f
				mode[n] = col_mode
				color[n] = column_color
				shape[n] = column_shape
				column_nodes.append(n)
			row_mode = self.dataSet['Row header mode']
			line = fp.readline()
			while line != '':
				row_entries = line.split(entry_separator)
				n = self.graph.addNode()
				label[n] = row_entries[0]
				mode[n] = row_mode
				color[n] = line_color
				shape[n] = line_shape
				row_entries.pop(0)
				for i, entry in enumerate(row_entries):
					if entry != '':
						self.graph.addEdge(n, column_nodes[i])
				line = fp.readline()
		return True

# The line below does the magic to register the plugin to the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPluginOfGroup("ImportTwoMode", "Two Mode Network", "G. Melancon", "08/06/2016", "", "1.0", "File")
